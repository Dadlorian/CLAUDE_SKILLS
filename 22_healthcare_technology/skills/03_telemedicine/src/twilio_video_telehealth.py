"""
Twilio Video Telehealth Implementation
Production-ready Python implementation for custom telehealth video rooms
"""

import os
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from datetime import datetime, timedelta

class TwilioTelehealthService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.api_key_sid = os.getenv('TWILIO_API_KEY_SID')
        self.api_key_secret = os.getenv('TWILIO_API_KEY_SECRET')
        self.client = Client(self.account_sid, self.auth_token)

    def create_video_room(self, appointment_id, patient_id, provider_id):
        """Create a new video room for telehealth session"""
        room_name = f"appointment-{appointment_id}-{int(datetime.now().timestamp())}"

        try:
            room = self.client.video.rooms.create(
                unique_name=room_name,
                type='group',
                max_participants=2,
                record_participants_on_connect=True,
                status_callback=f"{os.getenv('API_URL')}/webhooks/twilio/room-status",
                video_codecs=['VP8'],
                media_region='us1'
            )

            return {
                'sid': room.sid,
                'name': room.unique_name,
                'status': room.status,
                'created_at': room.date_created
            }

        except Exception as e:
            print(f"Error creating video room: {str(e)}")
            raise

    def generate_access_token(self, user_id, room_name, ttl=3600):
        """Generate access token for participant to join room"""
        token = AccessToken(
            self.account_sid,
            self.api_key_sid,
            self.api_key_secret,
            identity=user_id,
            ttl=ttl
        )

        video_grant = VideoGrant(room=room_name)
        token.add_grant(video_grant)

        return token.to_jwt()

    def get_room_details(self, room_sid):
        """Get room status and details"""
        try:
            room = self.client.video.rooms(room_sid).fetch()
            return {
                'sid': room.sid,
                'name': room.unique_name,
                'status': room.status,
                'duration': room.duration,
                'participants': self.get_room_participants(room_sid)
            }
        except Exception as e:
            print(f"Error getting room details: {str(e)}")
            raise

    def get_room_participants(self, room_sid):
        """Get list of participants in room"""
        try:
            participants = self.client.video.rooms(room_sid).participants.list()
            return [
                {
                    'sid': p.sid,
                    'identity': p.identity,
                    'status': p.status,
                    'duration': p.duration
                }
                for p in participants
            ]
        except Exception as e:
            print(f"Error getting participants: {str(e)}")
            return []

    def end_room(self, room_sid):
        """Complete and close room"""
        try:
            room = self.client.video.rooms(room_sid).update(status='completed')
            return {'status': room.status, 'ended_at': datetime.now()}
        except Exception as e:
            print(f"Error ending room: {str(e)}")
            raise

    def get_recordings(self, room_sid):
        """Get recordings for a room"""
        try:
            recordings = self.client.video.recordings.list(room_sid=room_sid)
            return [
                {
                    'sid': r.sid,
                    'status': r.status,
                    'size': r.size,
                    'duration': r.duration,
                    'url': r.links['media']
                }
                for r in recordings
            ]
        except Exception as e:
            print(f"Error getting recordings: {str(e)}")
            return []
