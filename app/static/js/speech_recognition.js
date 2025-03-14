 // Start Dictation function (Speech Recognition)
 async function startDictation(targetInputId) {
    try {
        // Step 1: Fetch Speech API configuration from the backend
        const configResponse = await fetch('/api/get-speech-config');
        const configData = await configResponse.json();

        const subscriptionKey = configData.apiKey;
        const serviceRegion = configData.region;

        // Step 2: Ensure the keys exist
        if (!subscriptionKey || !serviceRegion) {
            console.error("Speech API key or region is missing.");
            alert("Speech API key or region is missing. Please check the console for details.");
            return;
        }

        // Step 3: Configure speech recognition
        var speechConfig = SpeechSDK.SpeechConfig.fromSubscription(subscriptionKey, serviceRegion);
        speechConfig.speechRecognitionLanguage = "fr-CA";

        var audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
        var recognizer = new SpeechSDK.SpeechRecognizer(speechConfig, audioConfig);

        // Log that recognition is starting
        
        alert("Starting speech recognition...");

        recognizer.recognizeOnceAsync(function (result) {
            alert("Speech recognition completed.");

            if (result.reason === SpeechSDK.ResultReason.RecognizedSpeech) {
                
                document.getElementById(targetInputId).value = result.text;

                // Optionally speak the text back to the user
                speakText(result.text);

            } else {
                console.error("Speech Recognition failed: " + result.errorDetails);
                alert("Speech recognition failed. Check the console for details.");
            }

        },
            function (err) {
                console.error("Error recognizing speech: " + err);
                alert("Error recognizing speech. Check the console for details.");
            });
    } catch (error) {
        console.error("Error starting speech recognition: ", error);
        alert("Error starting speech recognition. Check the console for details.");
    }
}


 // Text-to-Speech function
 async function speakText(text) {
    try {
        // Step 1: Fetch Speech API configuration from the backend
        const configResponse = await fetch('/api/get-speech-config');
        const configData = await configResponse.json();

        const subscriptionKey = configData.apiKey;
        const serviceRegion = configData.region;

        // Step 2: Ensure the keys exist
        if (!subscriptionKey || !serviceRegion) {
            console.error("Speech API key or region is missing.");
            alert("Speech API key or region is missing. Please check the console for details.");
            return;
        }

        // Step 3: Configure text-to-speech
        var speechConfig = SpeechSDK.SpeechConfig.fromSubscription(subscriptionKey, serviceRegion);
        speechConfig.speechSynthesisLanguage = "fr-CA";
        var audioConfig = SpeechSDK.AudioConfig.fromDefaultSpeakerOutput();
        var synthesizer = new SpeechSDK.SpeechSynthesizer(speechConfig, audioConfig);

        synthesizer.speakTextAsync(text,
            function (result) {
                if (result.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
                    
                } else {
                    console.error("Speech synthesis failed: " + result.errorDetails);
                }
                synthesizer.close();
            },
            function (err) {
                console.error("Error during speech synthesis: " + err);
                synthesizer.close();
            }
        );
    } catch (error) {
        console.error("Error during speech synthesis: ", error);
        alert("Error during speech synthesis. Check the console for details.");
    }
}