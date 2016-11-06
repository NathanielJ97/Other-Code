using System;

public class Person
{
	//Add variables here
	public String firstName;
	public String lastName;
	public String DOB;
	public String address;
	public Double telNumber;
	
	public Person()
	{
		//Default Constructor
	}		
	
	static void Main(string[] args)
	{
		Person New_Person = new Person();
		Person New_Person1 = new Person();
		Person New_Person2 = new Person();
		Contacts New_Contacts = new Contacts();
		New_Contacts.addContact(New_Person1);

		
		New_Person.setFirstName("George");
		New_Person.setLastName("Smith"); 
		New_Person.setTelNumber(87056075123); 		
		New_Person.setDOB("FLINTSTONE"); 
		
		Console.WriteLine(New_Person.firstName + " ");
		Console.WriteLine(New_Person.lastName + " ");
		Console.WriteLine(New_Person.telNumber + " ");
		Console.WriteLine(New_Person.DOB + " ");
		
		Console.WriteLine(New_Contacts.myContacts.firstName + " ");
		
		Console.WriteLine("Press Enter to terminate...");
		Console.Read();
	}
	
	//Add methods here
	public void setFirstName(String aFirstName)
	{
		firstName = aFirstName;
	}
	
	public void setLastName(String aLastName)
	{
		lastName = aLastName;
	}
	
	public void setTelNumber(Double aTelNumber)
	{
		telNumber = aTelNumber;
	}
	
	public void setDOB(String aDOB)
	{
		DOB = aDOB;
	}
}

public class Contacts
{
	//add variables here
	public Person[] myContacts = new Person[5];
	public int count = 0;
	
	public Contacts()
	{
		//Default Constructor
	}
		
	// Add methods here
	public void addContact(Person aPerson)
	{
	myContacts[count] = aPerson;
	count++;
	}
}