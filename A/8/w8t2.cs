using System;

class Calculator
{

public static void Main(string[] args)
{
	Console.WriteLine("~~~~~~ Acme Calculator-o-matic ~~~~~~");
	//Defining numbers and getting input
	Console.WriteLine("Enter two integers to add...");
	args[0] = Console.ReadLine();
	args[1] = Console.ReadLine();
	Console.WriteLine("Answer: {0}", Calculator.add(args[0], args[1]));
	
	Console.ReadLine();
}

//Calculator's Addition Method
private static double add(double a, double b)
{
	//return the values after being added
return (a + b);	
}
}