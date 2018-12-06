using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Windows.Speech;

public class SpeechRecognitionEngine : MonoBehaviour
{
	public string[] keywords = new string[] { "order this", "order two of these", "order three of these"};
	public ConfidenceLevel confidence = ConfidenceLevel.Low;

	public Text results;
    public PlayerInput player;

	protected PhraseRecognizer recognizer;
	protected string word = "";

	private void Start()
	{
		if (keywords != null)
		{
			recognizer = new KeywordRecognizer(keywords, confidence);
			recognizer.OnPhraseRecognized += Recognizer_OnPhraseRecognized;
			recognizer.Start();
		}
	}

	private void Recognizer_OnPhraseRecognized(PhraseRecognizedEventArgs args)
	{
		word = args.text;
		results.text = "You said: <b>" + word + "</b>";
        sendFeedback();
	}
	private void sendFeedback()
	{
		switch (word)
		{
			case "order this":
                player.attempOrder("1");
				break;
			case "order two of these":
                player.attempOrder("2");
                break;
			case "order three of these":
                player.attempOrder("3");
                break;
        }
        word = "";
	}

	private void OnApplicationQuit()
	{
		if (recognizer != null && recognizer.IsRunning)
		{
			recognizer.OnPhraseRecognized -= Recognizer_OnPhraseRecognized;
			recognizer.Stop();
		}
	}
}
