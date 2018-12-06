using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class Order {

	public string username = "patrick.nicoll@sap.com";
	public string productCode;
    public int quantity;

	public Order(string productCode, string quantity)
	{
		this.productCode = productCode;
        this.quantity = Int32.Parse(quantity);
	}

	
	
}
