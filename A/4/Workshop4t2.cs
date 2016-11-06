using System;

class Workshop4t2{

static void Main(){
	Console.Write("Enter 1 for F to C. Enter 2 for C to F");
	int userDecision = Convert.ToInt32(Console.ReadLine());
	Console.Write("Enter the value to be converted:");
	int value = Convert.ToInt32(Console.ReadLine());	
	int newValue = 0;
	
	switch (userDecision){
		
		case 1:
		//F to C
		newValue = 5 * (value - 32) / 9;
		Console.WriteLine("{0} is your value in C", newValue);
		break;
		
		case 2:
		//C to F
		newValue = (9 / 5) * value + 32;
		Console.WriteLine("{0} is your value in F", newValue);
		break;
		
		default:
		//incase of wrong input
		Console.WriteLine("Wrong Input Entered!!!");
		
		break;
	}

}

}