using System;

class Workshop3
{
	static void Main ()
	{
		//getting Property value
		Console.Write( "Please enter the value of your property: ");
		int propertyValue = Convert.ToInt32(Console.ReadLine());
		double stampDutyrate = 0;
		//getting appropriate stampDutyrate and displaying propertyValue and stampDutyrate
		Console.WriteLine("Property Value: £{0}", propertyValue);
		
		if (propertyValue < 150001)
		{
			stampDutyrate = 0;
			Console.WriteLine("Stamp Duty Rate: {0}%", stampDutyrate);
		}
		else if (propertyValue > 150000 && propertyValue < 250001 )
		{
			stampDutyrate = 1;
			Console.WriteLine("Stamp Duty Rate: {0}%", stampDutyrate);
		}
		else if (propertyValue > 250000 && propertyValue < 500001 )
		{
			stampDutyrate = 3;
			Console.WriteLine("Stamp Duty Rate: {0}%", stampDutyrate);
		}
		else if ( propertyValue > 500000 )
		{
			stampDutyrate = 4;
			Console.WriteLine("Stamp Duty Rate: {0}%", stampDutyrate);
		}
		
		
		
		//Calculating the amount of duty to pay
		double amountToPay = propertyValue * (stampDutyrate / 100);
		Console.WriteLine("The amount of duty to pay on this property is: £{0}", amountToPay);
		
	}
}