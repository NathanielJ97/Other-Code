using System;

class ExceptionTest
{

public static void Main()
{
	//Declaring variables
int number1 = 0;
int number2 = 0;

Console.WriteLine("Please Enter a value for Number1 and Number2:");
bool Flag = true;

while (Flag == true)
{
//try and catch exception
try
{
	//Read input and allocate to variables
number1 = Convert.ToInt32(Console.ReadLine());
number2 = Convert.ToInt32(Console.ReadLine());
}
catch(FormatException e)
{
	//Deal with exception
	Console.WriteLine("The following exception was caught: {0}", e);
}
Flag = false;
Console.WriteLine("Value for number1: {0} and the Value for number2: {1}", number1, number2);
}
}

}