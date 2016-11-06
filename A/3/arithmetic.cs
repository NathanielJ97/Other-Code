using System;

class arithmetic
{
	static void Main ( string[] args )
	{
		string firstNumber,
			   secondNumber;
			   
		decimal number1,
			number2;
		
		//getting first number from user as a string
		Console.Write( "Please enter your first integer: ");
		firstNumber = Console.ReadLine();
		
		//getting the second number from user as a string
		Console.Write( "\n Please enter your second integer: ");
		secondNumber = Console.ReadLine();
		
		//convert numbers from string to int
		number1 = Convert.ToDecimal( firstNumber );
		number2 = Convert.ToDecimal( secondNumber);
		
		//maths stuff
		decimal sum = number1 + number2;
		decimal difference = number1 - number2;
		decimal multiply = number1 * number2;
		decimal division = number1 / number2;
		decimal mod = number1 % number2;
		//average
		decimal average = (number1 + number2) / 2;
		
		//Display it
		Console.WriteLine( "\n {0} + {1} = {2}.", number1, number2, sum);
		Console.WriteLine( "\n {0} - {1} = {2}.", number1, number2, difference);
		Console.WriteLine( "\n {0} * {1} = {2}.", number1, number2, multiply);
		Console.WriteLine( "\n {0} / {1} = {2}.", number1, number2, division);
		Console.WriteLine( "\n {0} % {1} = {2}.", number1, number2, mod);
		Console.WriteLine( "\n average of {0} and {1} = {2}.", number1, number2, average);
		
		//if statements
		if (number1 > number2)
			Console.WriteLine( "\n {0} is greater than {1} .", number1, number2);
		
		if (number1 < number2)
			Console.WriteLine( "\n {0} is less than {1} .", number1, number2);
		
		if (number1 == number2)
			Console.WriteLine( "\n {0} is equal to {1} .", number1, number2);
	}// end of main method

}//end of class