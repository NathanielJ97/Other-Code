using System;

class ClassroomGrades{

public static void Main()
{
//Declaring array and Random
int[] gradeScore = new int[30];

Random r = new Random();
//Loop to assign values to each of the elements in the array
for (int i = 0; i < 30; i++)
{
//Randomly generating grade for each student
int generatedGrade = r.Next(0, 100);
gradeScore[i] = generatedGrade;

Console.WriteLine("Student {0} : {1}", i, gradeScore[i]);
}

}


}