import os, ssl, certifi, random, time
import urllib.request
import pydub
import speech_recognition
from typing import Optional
from playwright.sync_api import Page, Locator, expect

class CaptchaSolverFailedError(Exception):
    """Exception raised when captcha solving fails."""
    pass

class CaptchaSolver:
    """A class to solve reCAPTCHA challenges using audio recognition."""

    # Constants
    TEMP_DIR = "/tmp"
    TIMEOUT_STANDARD = 7
    TIMEOUT_SHORT = 1
    TIMEOUT_DETECTION = 0.5

    def __init__(self, page: Page) -> None:
        """Initialize the solver with a page.

        Args:
            page: Page instance for browser interaction
        """
        self.page = page

    def humanize_click(self, locator: Locator) -> None:
        """Perform a human-like click: random mouse movement, hover, short wait, then click."""
        box = locator.bounding_box()
        if box:
            jitter_x = box["x"] + random.uniform(1, box["width"] - 1)
            jitter_y = box["y"] + random.uniform(1, box["height"] - 1)
            self.page.mouse.move(jitter_x, jitter_y, steps=random.randint(8, 20))
            time.sleep(random.uniform(0.15, 0.5))
        locator.hover()
        time.sleep(random.uniform(0.1, 0.4))
        locator.click()

    def solve_captcha(self) -> None:
        """Attempt to solve the reCAPTCHA challenge.

        Raises:
            Exception: If captcha solving fails or bot is detected
        """
        frame = self.page.frame_locator('iframe[src*="recaptcha"]').first
        anchor = frame.locator("#recaptcha-anchor")

        self.humanize_click(anchor)

        # Check if bot was detected after clicking the checkbox
        if self.is_detected():
            raise CaptchaSolverFailedError("Bot detected after clicking checkbox.")

        # Check if challenge only requires checkbox click
        if self.is_solved():
            return
        
        print("Challenge requires more than checkbox click, proceeding to audio challenge...")

        # Open audio challenge
        challenge_frame = self.page.frame_locator('iframe[src*="bframe"]').first
        anchor = challenge_frame.locator("#recaptcha-audio-button")
        self.humanize_click(anchor)

        # Check if bot was detected after opening audio challenge
        if self.is_detected():
            raise CaptchaSolverFailedError("Bot detected after clicking audio challenge button.")

        # Download audio and transcribe
        print("Analyzing captcha audio")
        audio_src = challenge_frame.locator("#audio-source").get_attribute("src")

        if not audio_src:
            raise Exception("Audio challenge source in CAPTCHA not found")

        print("Verifying captcha")
        text_response = self._process_audio_challenge(audio_src)

        response_field = challenge_frame.locator("#audio-response")

        # Captcha errors-out so handle errors
        try:
            response_field.type(text_response.lower(), timeout=self.TIMEOUT_STANDARD)
        except:
            pass
        try: 
            response_field.press('Enter')
        except:
            pass

        # Check if bot was detected after entering audio response
        if self.is_detected():
            raise CaptchaSolverFailedError("Bot detected after entering audio response.")

        if not self.is_solved():
            raise CaptchaSolverFailedError("Failed to solve the captcha")
    
    def _process_audio_challenge(self, audio_url: str) -> str:
        """Process the audio challenge and return the recognized text.

        Args:
            audio_url: URL of the audio file to process

        Returns:
            str: Recognized text from the audio file
        """
        mp3_path = os.path.join(self.TEMP_DIR, f"{random.randrange(1,1000)}.mp3")
        wav_path = os.path.join(self.TEMP_DIR, f"{random.randrange(1,1000)}.wav")

        try:
            ctx = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(audio_url, context=ctx) as r, open(mp3_path, "wb") as f:
                f.write(r.read())
            sound = pydub.AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")

            recognizer = speech_recognition.Recognizer()
            with speech_recognition.AudioFile(wav_path) as source:
                audio = recognizer.record(source)

            return recognizer.recognize_google(audio)

        finally:
            for path in (mp3_path, wav_path):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass

    def is_solved(self) -> bool:
        """Check if the captcha has been solved successfully."""
        try:
            frame = self.page.frame_locator('iframe[src*="recaptcha"]').first

            # Check for harder challenge presence
            try:
                challenge = self.page.frame_locator('iframe[src*="bframe"]').first
                expect(challenge.locator("div").first).to_be_visible(timeout=500)
                return False
            except Exception:
                pass

            # No harder challenge found -> check for solved checkbox
            checkmark = frame.locator(".recaptcha-checkbox-checkmark")
            return checkmark.is_visible(timeout=int(self.TIMEOUT_SHORT * 1000))
        except Exception:
            return False

    def is_detected(self) -> bool:
        """Check if the bot has been detected."""
        try:
            challenge = self.page.frame_locator('iframe[src*="bframe"]').first
            expect(challenge.get_by_text("Try again later", exact=False)).to_be_visible(timeout=int(self.TIMEOUT_DETECTION * 1000))
            return True
        except Exception:
            return False
