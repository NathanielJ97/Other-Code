using System;

	namespace workshop5
	{
		{
				double cost = 0;

				if (quantity <= 50)
				{
					cost = quantity * 5.0;
				}
				if (quantity >= 51 && quantity <= 80)
				{
					cost = quantity * 4.0;
				}
				if (quantity >= 81 && quantity <= 100 || quantity > 100)
				{
					cost = quantity * 2.5;
				}
				return cost;

			{
				int counter = 1;
				while(counter <= 5)
				{
					Console.Write("{0}", counter);
					counter++;
				}
			}
		}
	}