using System;

class geometry
{
	public static void Main()
	{
		//main method
		Console.Write("Enter the radius of your circle: ");
		int radius = Convert.ToInt32(Console.ReadLine());
	    Console.Write("\nThe area is {0:f3}", circleArea(radius));
		
		//wait
		Console.ReadLine();
		
	}
	
	//Calculate the area of the circle
	public static double circleArea(int radius)
	{
		return (Math.PI * (radius * radius));
	}
	
}