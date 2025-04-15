import json
from datetime import datetime, timedelta
import uuid


class SessionManager:
    def __init__(self, session_file_path):
        self.session_file_path = session_file_path

    def _read_sessions(self):
        try:
            with open(self.session_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def _write_sessions(self, data):
        with open(self.session_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def create_session(self, email, educational_stage, topic=None):

        sessions = self._read_sessions()
        session_nonce = str(uuid.uuid4())
        current_time = datetime.now()

        # Initialize with enhanced metadata
        if email not in sessions:
            sessions[email] = {
                "current": educational_stage,
                "last_active": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                educational_stage: {"General chatbot": []}
            }
        elif educational_stage not in sessions[email]:
            sessions[email][educational_stage] = {"General chatbot": []}

        # Create new session with metadata
        new_session = {
            "session_nonce": session_nonce,
            "topic": topic,
            "content": [],
            "created_at": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_activity": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "questions_count": 0,
            "total_tokens": 0,
            "language": "ar"  # Default to Arabic for your history chatbot
        }

        sessions[email][educational_stage]["General chatbot"].append(
            new_session)
        sessions[email]["last_active"] = current_time.strftime(
            "%Y-%m-%d %H:%M:%S")

        self._write_sessions(sessions)
        return session_nonce

    def add_to_session(self, email, educational_stage, session_nonce, question, answer):
        sessions = self._read_sessions()
        current_time = datetime.now()

        if not self._validate_session_exists(sessions, email, educational_stage):
            return False

        chat_sessions = sessions[email][educational_stage]["General chatbot"]
        for session in chat_sessions:
            if session["session_nonce"] == session_nonce:
                session["content"].append({
                    "question": question,
                    "answer": answer,
                    "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "chat"  # Useful for different types of interactions
                })
                session["last_activity"] = current_time.strftime(
                    "%Y-%m-%d %H:%M:%S")
                session["questions_count"] += 1
                sessions[email]["last_active"] = current_time.strftime(
                    "%Y-%m-%d %H:%M:%S")
                self._write_sessions(sessions)
                return True
        return False

    def get_session(self, email, session_nonce):
        """Get complete session data by nonce."""
        sessions = self._read_sessions()

        if email not in sessions:
            return None

        # Search all educational stages for the session
        for stage in sessions[email]:
            if stage not in ["current", "last_active"]:
                for session in sessions[email][stage].get("General chatbot", []):
                    if session["session_nonce"] == session_nonce:
                        return session

        return None

    def clean_old_sessions(self, days_threshold=30):
        """Remove sessions older than the specified threshold."""
        sessions = self._read_sessions()
        current_time = datetime.now()
        threshold = current_time - timedelta(days=days_threshold)

        for email in list(sessions.keys()):
            for stage in list(sessions[email].keys()):
                if stage != "current" and stage != "last_active":
                    chat_sessions = sessions[email][stage].get(
                        "General chatbot", [])
                    active_sessions = []
                    for session in chat_sessions:
                        last_activity = datetime.strptime(
                            session["last_activity"], "%Y-%m-%d %H:%M:%S")
                        if last_activity > threshold:
                            active_sessions.append(session)
                    sessions[email][stage]["General chatbot"] = active_sessions

        self._write_sessions(sessions)

    def get_user_sessions(self, email):
        """Get all sessions for a user with metadata."""
        sessions = self._read_sessions()
        if email not in sessions:
            return []

        user_sessions = []
        for stage in sessions[email]:
            if stage not in ["current", "last_active"]:
                chat_sessions = sessions[email][stage].get("General chatbot", [])
                
                for session in chat_sessions:
                    try:
                        first_message = session["content"][0] if session["content"] else None
                        user_sessions.append({
                            "stage": stage,
                            "session_nonce": session["session_nonce"],
                            "topic": session.get("topic"),
                            "created_at": session["created_at"],
                            "last_activity": session["last_activity"],
                            "questions_count": session["questions_count"],
                            "first_question": first_message["question"] if first_message else "New Chat"
                        })
                    except Exception as e:
                        print(f"[SessionManager] Error processing session: {e}")
                        continue

        print(f"[SessionManager] Returning {len(user_sessions)} sessions")
        return user_sessions

    def _validate_session_exists(self, sessions, email, educational_stage):
        """Helper method to validate session structure exists."""
        return (email in sessions and
                educational_stage in sessions[email] and
                "General chatbot" in sessions[email][educational_stage])
