// static/js/speech_recognition.js

// ——————————————————————————————————————————————————————————————
// Speech Recognition + Text-to-Speech (TTS) via Azure Speech SDK
// Expects window.API.getSpeechConfig to be injected in base.html:
//   window.API = { getSpeechConfig: "{{ url_for('api.get_speech_config') }}", … }
// ——————————————————————————————————————————————————————————————

/**
 * Start one-shot speech recognition and write result into the given input.
 * @param {string} targetInputId  DOM id of the <input> to receive the transcript
 */
export async function startDictation(targetInputId) {
  try {
    // Fetch subscription info
    const resp = await fetch(window.API.getSpeechConfig);
    const { apiKey: subscriptionKey, region: serviceRegion } = await resp.json();

    if (!subscriptionKey || !serviceRegion) {
      console.error("Speech API key or region is missing.");
      alert("Speech API key or region is missing. See console for details.");
      return;
    }

    // Configure recognizer
    const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(subscriptionKey, serviceRegion);
    speechConfig.speechRecognitionLanguage = "fr-CA";
    const audioConfig  = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
    const recognizer   = new SpeechSDK.SpeechRecognizer(speechConfig, audioConfig);

    alert("Démarrage de la reconnaissance vocale…");

    recognizer.recognizeOnceAsync(
      result => {
        alert("Reconnaissance terminée.");

        if (result.reason === SpeechSDK.ResultReason.RecognizedSpeech) {
          const el = document.getElementById(targetInputId);
          if (el) el.value = result.text;
          speakText(result.text);
        } else {
          console.error("Échec reconnaissance :", result.errorDetails);
          alert("Échec de la reconnaissance. Voir console.");
        }
      },
      err => {
        console.error("Erreur de reconnaissance :", err);
        alert("Erreur durant la reconnaissance. Voir console.");
      }
    );
  } catch (err) {
    console.error("Impossible de démarrer la reconnaissance :", err);
    alert("Erreur de démarrage. Voir console.");
  }
}

/**
 * Speak a text string via Azure TTS.
 * @param {string} text  The text to voice out
 */
export async function speakText(text) {
  try {
    // Fetch subscription info
    const resp = await fetch(window.API.getSpeechConfig);
    const { apiKey: subscriptionKey, region: serviceRegion } = await resp.json();

    if (!subscriptionKey || !serviceRegion) {
      console.error("Speech API key or region is missing.");
      alert("Speech API key or region is missing. See console for details.");
      return;
    }

    // Configure synthesizer
    const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(subscriptionKey, serviceRegion);
    speechConfig.speechSynthesisLanguage = "fr-CA";
    const audioConfig   = SpeechSDK.AudioConfig.fromDefaultSpeakerOutput();
    const synthesizer  = new SpeechSDK.SpeechSynthesizer(speechConfig, audioConfig);

    synthesizer.speakTextAsync(
      result => {
        if (result.reason !== SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
          console.error("Synthèse vocale échouée :", result.errorDetails);
        }
        synthesizer.close();
      },
      err => {
        console.error("Erreur synthèse vocale :", err);
        synthesizer.close();
      }
    );
  } catch (err) {
    console.error("Erreur durant la synthèse :", err);
    alert("Erreur de synthèse. Voir console.");
  }
}
