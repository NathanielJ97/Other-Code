using System;

public class Workshop4t3{

public void Main(){
Console.Write("Please Enter a Grade Value between 0 and 100");
int gradeValue = Convert.ToInt32(Console.ReadLine());

if (gradeValue < 40){
	Console.Write("Fail");
} else if (gradeValue < 50) {
	Console.Write("Third Class (Grade D)");	
} else if (gradeValue < 60) {
	Console.Write("Lower Second (Grade C)");
} else if (gradeValue < 70) {
    Console.Write("Upper Second (Grade B)");
} else {
	Console.Write("First Class (Grade A)");
}

}

}