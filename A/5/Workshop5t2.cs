using System;

class Workshop5t2{

static void Main(){
double widgetCost = 5;
int widgetQuantity = 1;
double TotalCost = 0;

Console.Write("Please Enter a Value?");

while (widgetQuantity <= 50){
widgetCost = 5;
TotalCost = TotalCost + widgetCost;
widgetQuantity++;
}

while (widgetQuantity <= 80){
widgetCost = 4;
TotalCost = TotalCost + widgetCost;
widgetQuantity++;
}

while (widgetQuantity <= 100){
widgetCost = 2.50;
TotalCost = TotalCost + widgetCost;
widgetQuantity++;
}

Console.Write("Total Cost:{0} Widget Cost:{1}", TotalCost, widgetCost);
}

}

//put the whole program in a while loop and run if true; (to exit, call "break;")
//ask the user for an amout
//calulate this amount using the same method as you have already used
//ask user if they would like to input another values]
	// if "Y" use continue;
	//if "n" use break;