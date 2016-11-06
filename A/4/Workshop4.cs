using System;

class Workshop4
{
static void Main()
{
	Console.Write("Enter a whole number...");
	int userNumber = Convert.ToInt32(Console.ReadLine());
	int oddevenNumber = userNumber % 2;
	
	if (oddevenNumber > 0){
		Console.Write("Your value is odd!");
	}		else
		{
			Console.Write("Your value is even!");
		}
			Console.WriteLine("------------------------");
}
}