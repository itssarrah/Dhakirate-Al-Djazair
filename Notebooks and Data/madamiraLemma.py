import pandas as pd
import os
import xml.etree.ElementTree as ET
import re
import subprocess
import time
from typing import List
import logging
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MadamiraServer:
    """Manages the MADAMIRA server lifecycle with optimizations."""
    
    def __init__(self, jar_path: str = "MADAMIRA-release-20190603-2.1/MADAMIRA-release-20190603-2.1/MADAMIRA-release-20190603-2.1.jar"):
        self.jar_path = jar_path
        self.server_process = None
        self.restart_count = 0
        self.max_restarts = 3
        self.last_restart = time.time()
        self.processed_count = 0
        self.restart_threshold = 100  # Restart server every 100 processes
        
    def start(self) -> None:
        """Start the MADAMIRA server with improved memory settings."""
        if self.server_process is not None:
            self.stop()
        
        logger.info("Starting MADAMIRA server...")
        try:
            self.server_process = subprocess.Popen(
                ["java", "-Xmx4000m", "-Xms4000m", "-XX:NewRatio=3",
                 "-jar", self.jar_path, "-s"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(10)  # Give more time to start
            logger.info("MADAMIRA server started successfully")
            self.last_restart = time.time()
            self.processed_count = 0
        except Exception as e:
            logger.error(f"Failed to start MADAMIRA server: {str(e)}")
            raise
        
    def stop(self) -> None:
        """Stop the MADAMIRA server safely."""
        if self.server_process:
            logger.info("Stopping MADAMIRA server...")
            try:
                subprocess.run(
                    ["java", "-Xmx4000m", "-Xms4000m", "-XX:NewRatio=3",
                     "-jar", self.jar_path, "-k"],
                    check=True,
                    capture_output=True,
                    timeout=60
                )
                self.server_process.terminate()
                self.server_process = None
                logger.info("MADAMIRA server stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping MADAMIRA server: {str(e)}")
                if self.server_process:
                    self.server_process.kill()
                raise

    def restart_if_needed(self):
        """Restart server if it's processed too many items or if too much time has passed."""
        self.processed_count += 1
        current_time = time.time()
        
        if (self.processed_count >= self.restart_threshold or 
            current_time - self.last_restart > 3600):  # 1 hour
            logger.info("Performing scheduled server restart...")
            self.start()

    def process_with_retry(self, input_file: str, output_file: str, max_retries: int = 3) -> bool:
        """Process file with automatic retries and error handling."""
        for attempt in range(max_retries):
            try:
                self.restart_if_needed()
                subprocess.run(
                    ["java", "-Xmx4000m", "-Xms4000m", "-XX:NewRatio=3",
                     "-jar", self.jar_path,
                     "-c", "-i", input_file, "-o", output_file],
                    check=True,
                    capture_output=True,
                    timeout=300  # 5 minute timeout
                )
                return True
            except subprocess.TimeoutExpired:
                logger.warning(f"Process timed out on attempt {attempt + 1}")
                self.start()  # Restart server on timeout
            except Exception as e:
                logger.warning(f"Process failed on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed all retries for processing {input_file}")
                    return False
                time.sleep(5)  # Wait before retry
                self.start()  # Restart server on error
        return False

def generate_input_xml(content: str, filename: str = "input.xml") -> None:
    """Generate an input XML file for MADAMIRA."""
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<madamira_input xmlns="urn:edu.columbia.ccls.madamira.configuration:0.1">
    <madamira_configuration>
        <preprocessing sentence_ids="false" separate_punct="true" input_encoding="UTF8"/>
        <overall_vars output_encoding="UTF8" dialect="MSA" output_analyses="TOP" morph_backoff="NONE"/>
        <requested_output>
            <req_variable name="LEMMA" value="true" />
            <req_variable name="STEM" value="false" />
            <req_variable name="GLOSS" value="false" />
            <req_variable name="DIAC" value="false" />
            <req_variable name="ASP" value="false" />
            <req_variable name="CAS" value="false" />
            <req_variable name="ENC0" value="false" />
            <req_variable name="ENC1" value="false" />
            <req_variable name="ENC2" value="false" />
            <req_variable name="GEN" value="false" />
            <req_variable name="MOD" value="false" />
            <req_variable name="NUM" value="false" />
            <req_variable name="PER" value="false" />
            <req_variable name="POS" value="false" />
            <req_variable name="PRC0" value="false" />
            <req_variable name="PRC1" value="false" />
            <req_variable name="PRC2" value="false" />
            <req_variable name="PRC3" value="false" />
            <req_variable name="STT" value="false" />
            <req_variable name="VOX" value="false" />
            <req_variable name="BW" value="false" />
            <req_variable name="SOURCE" value="false" />
            <req_variable name="BPC" value="false" />
            <req_variable name="NER" value="false" />
        </requested_output>
        <tokenization>
            <scheme alias="ATB" />
        </tokenization>
    </madamira_configuration>

    <in_doc id="ExampleDocument">
        <in_seg id="SENT1">{content}</in_seg>
    </in_doc>
</madamira_input>'''.format(content=content)

    try:
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(xml_content)
        logger.info(f"Input XML file generated successfully: {filename}")
    except Exception as e:
        logger.error(f"Error generating input XML: {str(e)}")
        raise

def extract_clean_lemmas(output_file: str) -> List[str]:
    """Extract and clean lemmatized sentences from output XML."""
    try:
        tree = ET.parse(output_file)
        root = tree.getroot()

        ns = {'ns': 'urn:edu.columbia.ccls.madamira.configuration:0.1'}
        lemmatized_sentences = []
        arabic_pattern = re.compile(r'[^\u0600-\u06FF\u0660-\u0669\s]')

        for segment in root.findall(".//ns:out_seg", ns):
            lemmas = []
            for word in segment.findall(".//ns:word", ns):
                lemma_element = word.find(".//ns:morph_feature_set[@lemma]", ns)
                if lemma_element is not None:
                    lemma = lemma_element.get("lemma")
                    clean_lemma = arabic_pattern.sub('', lemma).strip()
                    if clean_lemma:  # Only add non-empty lemmas
                        lemmas.append(clean_lemma)
            if lemmas:  # Only add non-empty sentences
                lemmatized_sentences.append(" ".join(lemmas))

        return lemmatized_sentences
    except Exception as e:
        logger.error(f"Error extracting lemmas: {str(e)}")
        raise

def batch_process(texts: List[str], batch_size: int = 10) -> List[str]:
    """Process texts in batches with error handling."""
    server = MadamiraServer()
    server.start()
    results = []
    
    try:
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = []
            
            for idx, text in enumerate(batch):
                input_file = f"input_{idx}.xml"
                output_file = f"output_{idx}.xml"
                
                try:
                    generate_input_xml(text, input_file)
                    if server.process_with_retry(input_file, output_file):
                        lemmas = extract_clean_lemmas(output_file)
                        batch_results.append(" ".join(lemmas))
                    else:
                        batch_results.append("")  # Empty string for failed processing
                except Exception as e:
                    logger.error(f"Error processing text: {str(e)}")
                    batch_results.append("")
                finally:
                    # Clean up files
                    for file in [input_file, output_file]:
                        if os.path.exists(file):
                            try:
                                os.remove(file)
                            except Exception:
                                pass
            
            results.extend(batch_results)
            
    finally:
        server.stop()
    
    return results

def madamira_lemmatize_dataframe(
    df: pd.DataFrame,
    input_col: str,
    output_col: str,
    batch_size: int = 10,
    jar_path: str = None
) -> pd.DataFrame:
    """
    Main function to lemmatize DataFrame content with progress tracking.
    
    Args:
        df: Input DataFrame
        input_col: Name of input column containing Arabic text
        output_col: Name of output column for lemmatized text
        batch_size: Number of texts to process in each batch
        jar_path: Optional path to MADAMIRA JAR file
    
    Returns:
        DataFrame with added column containing lemmatized text
    """
    texts = df[input_col].tolist()
    total_batches = (len(texts) + batch_size - 1) // batch_size
    
    logger.info(f"Processing {len(texts)} texts in {total_batches} batches")
    
    try:
        # Process in batches with progress bar
        with tqdm(total=len(texts), desc="Lemmatizing") as pbar:
            results = batch_process(texts, batch_size)
            pbar.update(len(texts))
        
        # Add results to DataFrame
        df[output_col] = results
        
        # Report success rate
        success_count = sum(1 for r in results if r)
        logger.info(f"Processing complete. Success rate: {success_count}/{len(texts)} "
                   f"({success_count/len(texts)*100:.1f}%)")
        
    except Exception as e:
        logger.error(f"Error during batch processing: {str(e)}")
        raise
        
    return df
def madamira_lemmatize_text(
    text,
    batch_size: int = 10,
    jar_path: str = None
):
    # Wrap the string in a list if it's not already a list or array-like
    if isinstance(text, str):
        texts = [text]
    else:
        texts = text.tolist()
        
    total_batches = (len(texts) + batch_size - 1) // batch_size
    
    logger.info(f"Processing {len(texts)} texts in {total_batches} batches")
    
    try:
        # Process in batches with progress bar
        with tqdm(total=len(texts), desc="Lemmatizing") as pbar:
            results = batch_process(texts, batch_size)
            pbar.update(len(texts))
        
        # Report success rate
        success_count = sum(1 for r in results if r)
        logger.info(f"Processing complete. Success rate: {success_count}/{len(texts)} "
                   f"({success_count/len(texts)*100:.1f}%)")
        
    except Exception as e:
        logger.error(f"Error during batch processing: {str(e)}")
        raise
        
    return results

"""
def main():
    #Example usage of the MADAMIRA lemmatization system.
    try:
        # Sample DataFrame
        data = {
            'arabic_text': [
                'السلطة الفلسطينية تستنكر استمرار سياسة الاغتيالات الاسرائي',
                'غزة 1 - 11 ( اف ب ) - استنكرت السلطة الوطنية الفلسطينية اليوم الخميس استمرار سياسة الاغتيالات وعمليات قتل الفلسطينيين',
                'ويستمر غياب ينز يريميز ويورغ هاينريخ ومحمد شول'
            ]
        }
        df = pd.DataFrame(data)

        # Lemmatize the text
        result_df = madamira_lemmatize_dataframe(
            df,
            input_col='arabic_text',
            output_col='lemmatized_text',
            batch_size=10
        )

        # Display results
        print("\nOriginal and lemmatized texts:")
        for idx, row in result_df.iterrows():
            print(f"\nText {idx + 1}:")
            print(f"Original: {row['arabic_text']}")
            print(f"Lemmatized: {row['lemmatized_text']}")

    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    main()

"""