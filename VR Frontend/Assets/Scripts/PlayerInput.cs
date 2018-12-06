using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerInput : MonoBehaviour {

	public GameObject item1Details;
	public GameObject item1Notification;
	public OVRGrabbable item1;

	public GameObject item2Details;
	public GameObject item2Notification;
	public OVRGrabbable item2;

	public GameObject item3Details;
	public GameObject item3Notification;
	public OVRGrabbable item3;

	public PostRequest postRequest;

	private Vector3 item1OrigPosition;
	private Quaternion item1OrigRotation;
	private Vector3 item2OrigPosition;
	private Quaternion item2OrigRotation;
	private Vector3 item3OrigPosition;
	private Quaternion item3OrigRotation;

	// Use this for initialization
	void Start () {
		item1OrigPosition = item1.transform.position;
		item1OrigRotation = item1.transform.rotation;

		item2OrigPosition = item2.transform.position;
		item2OrigRotation = item2.transform.rotation;

		item3OrigPosition = item3.transform.position;
		item3OrigRotation = item3.transform.rotation;
	}
	
	// Update is called once per frame/gugg
	void Update () {
		if (item1.isGrabbed)
		{
			item1Details.SetActive(true);

			if (OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger))
			{
				item1Notification.SetActive(true);
				postRequest.request("1990255", "1", item1Notification);
			}
		}
		else if (!item1.isGrabbed)
		{
			item1Details.SetActive(false);
			item1.transform.position = item1OrigPosition;
			item1.transform.rotation = item1OrigRotation;
		}

		if (item2.isGrabbed)
		{
			item2Details.SetActive(true);

			if (OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger))
			{
				item2Notification.SetActive(true);
				postRequest.request("1776948", "1", item2Notification);
			}
		}
		else if (!item2.isGrabbed)
		{
			item2Details.SetActive(false);
			item2.transform.position = item2OrigPosition;
			item2.transform.rotation = item2OrigRotation;
		}

		if (item3.isGrabbed)
		{
			item3Details.SetActive(true);

			if (OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger))
			{
				item3Notification.SetActive(true);
				postRequest.request("266899", "1", item3Notification);
			}
		}
		else if (!item3.isGrabbed)
		{
			item3Details.SetActive(false);
			item3.transform.position = item3OrigPosition;
			item3.transform.rotation = item3OrigRotation;
		}
	}

    public void attempOrder(string qty)
    {
        if (item1.isGrabbed)
        {
            item1Notification.SetActive(true);
            postRequest.request("1990255", qty, item1Notification);
        }
        else if(item2.isGrabbed)
        {
            item2Notification.SetActive(true);
            postRequest.request("1776948", qty, item2Notification);
        }
        else if (item3.isGrabbed)
        {
            item3Notification.SetActive(true);
            postRequest.request("266899", qty, item3Notification);
        }
    }
}
