from flask import Blueprint, request, jsonify
from app.chat import answer_question_with_relevant_content_GN
from app.session_manager import SessionManager
from app.user_manager import UserManager
from app.ml_manager import MLManager
from app.quiz_manager import QuizManager
from app.progress_manager import ProgressManager
from app.personality_quiz_manager import PersonalityQuizManager
from app.personality_progress_manager import PersonalityProgressManager
from app.events_quiz_manager import EventsQuizManager
from app.events_progress_manager import EventsProgressManager
from app.topic_manager import TopicManager
import json

bp = Blueprint('routes', __name__)

# Initialize managers
ml_manager = MLManager()
session_manager = SessionManager("sessions.json")
user_manager = UserManager("users.json")
progress_manager = ProgressManager("progress.json")
quiz_manager = QuizManager(ml_manager)
personality_quiz_manager = PersonalityQuizManager()
personality_progress_manager = PersonalityProgressManager()
events_quiz_manager = EventsQuizManager()
events_progress_manager = EventsProgressManager()
topic_manager = TopicManager(ml_manager)


@bp.route('/signup', methods=['POST'])
def signup():
    payload = request.get_json()
    email = payload.get('email')
    password = payload.get('password')
    firstname = payload.get('firstname')
    educational_level = payload.get('educational_level')

    if not all([email, password, firstname, educational_level]):
        return jsonify({"error": "Missing required fields"}), 400

    success, message = user_manager.create_user(
        email, password, firstname, educational_level)

    if success:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400


@bp.route('/login', methods=['POST'])
def login():
    payload = request.get_json()
    email = payload.get('email')
    password = payload.get('password')

    if not all([email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    success, result = user_manager.verify_user(email, password)

    if success:
        return jsonify({"user": result}), 200
    return jsonify({"error": result}), 401


@bp.route('/ask', methods=['POST', 'OPTIONS'])
def ask_question():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    payload = request.get_json()
    email = payload.get('email')
    question = payload.get('question')
    educational_stage = payload.get('educational_stage')
    historical_era = payload.get('historical_era', None)
    session_nonce = payload.get('session_nonce', None)
    topic = payload.get('topic', None)

    if not email or not question:
        return jsonify({"error": "Missing required fields"}), 400

    if not session_nonce or session_nonce == "None":
        session_nonce = session_manager.create_session(
            email, educational_stage, topic)

        # Check cache first
    cached = ml_manager.get_cached_response(question)
    if cached:
        # Still log to session but return cached
        session_manager.add_to_session(
            email, EducationalStage, session_nonce, question, cached)
        return jsonify({
            "session_nonce": session_nonce,
            "answer": cached
        }), 200

    answer = answer_question_with_relevant_content_GN(
        email=email,
        query=question,
        data=ml_manager.get_data(),
        session_manager=session_manager,
        model=ml_manager.get_model(),
        session_nonce=session_nonce,
        EducationalStage=educational_stage,
        HistoricalEra=historical_era,
        Topic=topic
    )

    return jsonify({
        "session_nonce": session_nonce,
        "answer": answer
    }), 200


@bp.route('/sessions', methods=['GET'])
def get_user_sessions():
    email = request.args.get('email')

    if not email:
        return jsonify({"error": "Missing email parameter"}), 400

    sessions = session_manager.get_user_sessions(email)
    return jsonify({"sessions": sessions}), 200


@bp.route('/quiz/generate', methods=['POST'])
def generate_quiz():
    payload = request.get_json()
    email = payload.get('email')
    educational_stage = payload.get('educational_stage')
    level = payload.get('level')
    num_questions = payload.get('num_questions', 5)
    use_cache = payload.get('use_cache', True)  # Add cache control

    if not all([email, educational_stage, level]):
        return jsonify({"error": "Missing required fields"}), 400
    print(f"Generating quiz for {email} in {educational_stage} level {level}")
    # Check cache first if enabled
    if use_cache:
        email = "student@example.com"
        educational_stage = "HSS3"
        try:
            with open('quiz_cache.json', 'r', encoding='utf-8') as f:
                cache = json.load(f)
                if (email in cache and 
                    educational_stage in cache[email] and 
                    str(level) in cache[email][educational_stage]):
                    cached_quiz = cache[email][educational_stage][str(level)]['quiz']
                    return jsonify({
                        "quiz": cached_quiz,
                        "total_questions": len(cached_quiz),
                        "cached": True
                    }), 200
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Cache error: {str(e)}")
            # Continue with normal quiz generation if cache fails

    # If not in cache or cache disabled, generate normally
    answered_questions = progress_manager.get_answered_questions(
        email, educational_stage, level)

    quiz = quiz_manager.generate_quiz(
        educational_stage,
        level,
        answered_questions,
        num_questions=num_questions
    )

    # if parsing fails the quiz will be none, so attempt 3 times to generate again
    if not quiz:
        for i in range(3):
            quiz = quiz_manager.generate_quiz(
                educational_stage,
                level,
                answered_questions,
                num_questions=num_questions
            )
            if quiz:
                break

    return jsonify({
        "quiz": quiz,
        "total_questions": len(quiz),
        "cached": False
    }), 200


@bp.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    payload = request.get_json()
    email = payload.get('email')
    educational_stage = payload.get('educational_stage')
    level = payload.get('level')
    answers = payload.get('answers')  # {question_id: selected_option}
    quiz_data = payload.get('quiz_data')

    if not all([email, educational_stage, level, answers, quiz_data]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        start_time = payload.get('start_time')  # Add timestamp tracking
        end_time = payload.get('end_time')
        
        results = []
        total_correct = 0
        total_incorrect = 0
        last_progress = None
        
        for question_id, selected_option in answers.items():
            try:
                question_id = int(question_id)
                is_correct = quiz_manager.evaluate_answer(
                    question_id, selected_option, quiz_data)
                    
                if is_correct:
                    total_correct += 1
                else:
                    total_incorrect += 1
                    
                result = {
                    "question_id": question_id,
                    "correct": is_correct,
                }
                
                question = next(q for q in quiz_data if q['id'] == question_id)
                progress = progress_manager.update_progress(
                    email, educational_stage, level,
                    question['question'], is_correct
                )
                last_progress = progress  # Save the last progress update
                
                results.append({
                    "question_id": question_id,
                    "correct": is_correct,
                    "progress": progress
                })

            except ValueError as e:
                print(f"Error processing question {question_id}: {str(e)}")
                results.append({"question_id": question_id, "correct": False, "error": "Invalid data"})

        # Get final level progress
        final_progress = progress_manager.calculate_level_progress(
            email, educational_stage, level)

        summary = {
            "total_questions": len(answers),
            "correct_answers": total_correct,
            "incorrect_answers": total_incorrect,
            "accuracy": (total_correct / len(answers)) * 100 if answers else 0,
            "time_taken": end_time - start_time if start_time and end_time else None,
            "final_progress": final_progress  # Add final progress to summary
        }
        
        # Add mastery stats to the response
        mastery_stats = progress_manager.get_mastery_stats(
            email, educational_stage, level)
        
        return jsonify({
            "results": results,
            "summary": summary,
            "level_progress": final_progress,
            "mastery_stats": mastery_stats
        }), 200
        
    except Exception as e:
        print(f"Error submitting quiz: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@bp.route('/quiz/progress', methods=['GET'])
def get_stage_progress():
    """Returns progress for all levels in a given educational stage"""
    try:
        email = request.args.get('email')
        educational_stage = request.args.get('educational_stage')

        if not all([email, educational_stage]):
            return jsonify({
                "error": "Missing required fields",
                "progress": {str(i): {"progress": 0, "mastery_score": 0} for i in range(1, 4)}
            }), 400

        progress = progress_manager.get_stage_progress(email, educational_stage)
        
        return jsonify({
            "progress": progress
        }), 200
        
    except Exception as e:
        print(f"Progress endpoint error: {str(e)}")
        # Return default progress on error
        return jsonify({
            "progress": {str(i): {"progress": 0, "mastery_score": 0} for i in range(1, 4)}
        }), 200


@bp.route('/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics across all stages or for a specific stage"""
    email = request.args.get('email')
    educational_stage = request.args.get('educational_stage', None)  # Optional

    if not email:
        return jsonify({"error": "Missing email parameter"}), 400

    stats = progress_manager.get_user_stats(email, educational_stage)
    return jsonify({"stats": stats}), 200


@bp.route('/personality/quiz/generate', methods=['POST'])
def generate_personality_quiz():
    payload = request.get_json()
    email = payload.get('email')
    educational_stage = payload.get('educational_stage')
    num_questions = payload.get('num_questions', 4)

    if not all([email, educational_stage]):
        return jsonify({"error": "Missing required fields"}), 400

    solved_questions = personality_progress_manager.get_solved_questions(
        email, educational_stage)

    quiz = personality_quiz_manager.generate_quiz(
        educational_stage,
        solved_questions,
        num_questions
    )

    return jsonify({
        "quiz": quiz,
        "total_questions": num_questions
    }), 200

@bp.route('/personality/quiz/submit', methods=['POST'])
def submit_personality_quiz():
    payload = request.get_json()
    email = payload.get('email')
    educational_stage = payload.get('educational_stage')
    matches = payload.get('matches')  # List of {personality_id, description_id}

    if not all([email, educational_stage, matches]):
        return jsonify({"error": "Missing required fields"}), 400

    results = []
    for match in matches:
        is_correct = personality_quiz_manager.validate_answer(
            match['personality_id'],
            match['description_id']
        )
        
        if is_correct:
            # Get the personality data from the quiz data
            personality_data = {
                'name': match['personality_name'],
                'description': match['description'],
                'image_link': match['image_link'] if 'image_link' in match else None
            }
            
            progress = personality_progress_manager.update_progress(
                email,
                educational_stage,
                match['personality_id'],
                personality_data
            )
            
        results.append({
            "personality_id": match['personality_id'],
            "correct": is_correct
        })

    return jsonify({
        "results": results,
        "progress": personality_progress_manager.get_solved_questions(email, educational_stage)
    }), 200

@bp.route('/personality/progress', methods=['GET'])
def get_personality_progress():
    email = request.args.get('email')
    educational_stage = request.args.get('educational_stage')

    if not all([email, educational_stage]):
        return jsonify({"error": "Missing required fields"}), 400

    progress = personality_progress_manager.get_solved_questions(email, educational_stage)
    return jsonify({"progress": progress}), 200

@bp.route('/events/quiz/generate', methods=['POST'])
def generate_events_quiz():
    payload = request.get_json()
    email = payload.get('email')
    educational_stage = payload.get('educational_stage')
    num_questions = payload.get('num_questions', 5)

    if not all([email, educational_stage]):
        return jsonify({"error": "Missing required fields"}), 400

    solved_questions = events_progress_manager.get_solved_questions(
        email, educational_stage)

    quiz = events_quiz_manager.generate_quiz(
        educational_stage,
        solved_questions,
        num_questions
    )

    if not quiz:
        return jsonify({"error": "No more available questions"}), 404

    return jsonify({
        "quiz": quiz,
        "total_questions": len(quiz)
    }), 200

@bp.route('/events/quiz/submit', methods=['POST'])
def submit_events_quiz():
    payload = request.get_json()
    email = payload.get('email')
    educational_stage = payload.get('educational_stage')
    answers = payload.get('answers')  # List of {question_id, answer, type}

    if not all([email, educational_stage, answers]):
        return jsonify({"error": "Missing required fields"}), 400

    results = []
    for answer in answers:
        question_id = answer['question_id']
        answer_text = answer['answer']
        question_type = answer['type']
        
        # Get original question data
        question_data = events_quiz_manager.data.loc[question_id]
        
        is_correct = False
        if question_type == 0:  # date->event
            # Convert answer to embedding using the same model as quiz manager
            answer_embedding = ml_manager.get_model().encode(answer_text)
            is_correct = events_quiz_manager.validate_event_answer(
                answer_embedding, question_id)
        else:  # event->date
            is_correct = events_quiz_manager.validate_date_answer(
                answer_text, question_data['Date'])

        progress = events_progress_manager.update_progress(
            email,
            educational_stage,
            {
                "date": question_data['Date'],
                "event": question_data['Content']
            },
            is_correct
        )
        
        results.append({
            "question_id": question_id,
            "correct": is_correct,
            "progress": progress
        })

    return jsonify({
        "results": results
    }), 200

@bp.route('/events/progress', methods=['GET'])
def get_events_progress():
    email = request.args.get('email')
    educational_stage = request.args.get('educational_stage')

    if not all([email, educational_stage]):
        return jsonify({"error": "Missing required fields"}), 400

    progress = events_progress_manager.get_solved_questions(email, educational_stage)
    total_events = len(events_quiz_manager.data[
        events_quiz_manager.data['Educational stage'] == educational_stage
    ])
    
    stats = {
        "solved_questions": progress,
        "total_events": total_events,
        "mastery_percentage": (len(progress) / total_events * 100) if total_events > 0 else 0
    }
    
    return jsonify({"progress": stats}), 200

@bp.route('/topics', methods=['GET'])
def get_topics():
    educational_stage = request.args.get('educational_stage')
    
    if not educational_stage:
        return jsonify({"error": "Missing educational_stage parameter"}), 400

    try:
        data = ml_manager.get_data()
        # Filter out NaN and None values before getting unique topics
        topics = data[
            (data['EducationalStage'] == educational_stage) & 
            (data['Topic'].notna()) &
            (data['Topic'].notnull())  # Filter out NaN and null values
            & (data['Topic'] != "")  # Filter out empty strings
        ]['Topic'].unique().tolist()
        
        # Additional filtering and cleaning
        formatted_topics = [
            {
                'id': str(idx + 1),
                'title': str(topic).strip()
            }
            for idx, topic in enumerate(topics)
            if topic and isinstance(topic, (str, int, float)) and str(topic).strip() != 'nan'  # Extra check for 'nan' strings
        ]
        
        return jsonify({"topics": formatted_topics}), 200
    except Exception as e:
        print(f"Error fetching topics: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@bp.route('/topic-content', methods=['GET'])
def get_topic_content():
    educational_stage = request.args.get('educational_stage')
    topic_title = request.args.get('topic')  # Changed from topic_id to topic
    
    if not all([educational_stage, topic_title]):
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        data = ml_manager.get_data()
        topic_data = data[
            (data['EducationalStage'] == educational_stage) & 
            (data['Topic'] == topic_title)  # Direct topic title matching
        ]
        
        if topic_data.empty:
            return jsonify({"error": "Topic content not found"}), 404
            
        content = topic_data['Content'].iloc[0]
        # Pass educational_stage to enable caching
        enhanced_content = topic_manager.enhance_topic_content(
            topic_title, 
            content,
            educational_stage=educational_stage
        )
        
        return jsonify({
            "title": topic_title,
            "content": enhanced_content
        }), 200
    except Exception as e:
        print(f"Error fetching topic content: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/update_profile', methods=['POST'])
def update_profile():
    payload = request.get_json()
    email = payload.get('email')
    firstname = payload.get('firstname')
    educational_level = payload.get('educational_level')

    if not all([email, firstname, educational_level]):
        return jsonify({"error": "Missing required fields"}), 400

    user = user_manager.update_user(
        email, firstname, educational_level)

    return jsonify({"user": user}), 200

@bp.route('/quiz/detailed-stats', methods=['GET'])
def get_detailed_stats():
    """Get detailed quiz statistics using comprehensive user stats"""
    email = request.args.get('email')
    
    if not email:
        return jsonify({"error": "Missing email parameter"}), 400
        
    try:
        stats = progress_manager.get_user_stats(email)
        if not stats:
            return jsonify({"error": "No statistics found"}), 404

        # Transform the stats into the expected format for Taqarir
        formatted_stats = {}
        for stage_code, stage_data in stats['stages_progress'].items():
            stage_stats = {}
            for level, level_data in stage_data['levels'].items():
                stage_stats[f"المستوى {level}"] = [
                    level_data['correct_answers'],
                    level_data['incorrect_answers'],
                    f"{level_data['accuracy']:.0f}%"
                ]
            formatted_stats[stage_code] = stage_stats

        return jsonify({"statistics": formatted_stats}), 200
        
    except Exception as e:
        print(f"Error getting detailed stats: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/session-content', methods=['GET'])
def get_session_content():
    email = request.args.get('email')
    session_nonce = request.args.get('session_nonce')
    
    print(f"[Routes] Getting session content: email={email}, nonce={session_nonce}")
    
    if not email or not session_nonce:
        return jsonify({"error": "Missing required parameters"}), 400
        
    session = session_manager.get_session(email, session_nonce)
    if not session:
        return jsonify({
            "error": "Session not found",
            "content": []
        }), 200  # Return empty content instead of 404
        
    return jsonify({"content": session["content"]}), 200

