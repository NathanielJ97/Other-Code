using System;

class geometry
{
	public static void Main()
	{
		//main method
		Console.Write("Enter the radius of your circle: ");
		int radius = Convert.ToInt32(Console.ReadLine());
	    Console.Write("\nThe area is {0:f3}", circleArea(radius));
		//triangle
		Console.Write("\nEnter the base length of your triangle:");
		int tBase = Convert.ToInt32(Console.ReadLine());
		Console.Write("\nEnter the height of your triangle:");
		int tHeight = Convert.ToInt32(Console.ReadLine());
		Console.Write("\nThe area of your triangle is {0:f3}", triangleArea(tHeight, tBase));
		
		//wait
		Console.ReadLine();
		
	}
	
	//Calculate the area of the circle
	public static double circleArea(int radius)
	{
		return (Math.PI * (radius * radius));
	}
	
	//Calculate the area of the triangle
	public static double triangleArea (int tHeight, int tBase)
	{
	return (0.5 * (tBase * tHeight));
	}
}