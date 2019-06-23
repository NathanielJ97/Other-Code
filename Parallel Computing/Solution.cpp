///////////////////////////////////////
//CMP3103M - Parallel Computing////////
//Assignment Item 1 - Weather Summary//
//JOS13502565 - Nathaniel Josephs//////
//Solution.cpp/////////////////////////
///////////////////////////////////////

#define CL_USE_DEPRECATED_OPENCL_1_2_APIS
#define __CL_ENABLE_EXCEPTIONS

#include <iostream>
#include <vector>
#include <chrono> //For Timing Read & Total Run Speeds

#ifdef __APPLE__
#include <OpenCL/cl.hpp>
#else
#include <CL/cl.hpp>
#endif

#include "Utils.h"

using namespace std;

void print_help() {
	std::cerr << "Application usage:" << std::endl;

	std::cerr << "  -p : select platform " << std::endl;
	std::cerr << "  -d : select device" << std::endl;
	std::cerr << "  -l : list all platforms and devices" << std::endl;
	std::cerr << "  -h : print this message" << std::endl;
}

//READ DATA/FILE FUNCTION FOR READING THE TEMPERATURE TEXT FILES //this will need to be modified to accommodate for decimals at some point
vector<int>* ReadData(string fileName)
{
	vector<int>* data = new vector<int>;
	int i = 0;
	string value;
	ifstream file(fileName);

	//Check if file is currently open. If not, there is something preventing the file from being opened
	if (file.is_open())
	{
		//Repeat until every line in the file has been read
		while (!file.eof())
		{
			file >> value;
			//Get the correct column(6th Column = air temperature, degree Celsius) of data, store it as string
			if (i == 5)
			{
				data->push_back(int(stof(value) * 10));
				i = 0;
				continue;
			}
			i++; //Increment the counter
		}
		file.close(); //Close the file once EOF has been reached
		cout << "Read data from file!" << endl;
	}
	else
	{
		cout << "Issue preventing the file from being opened!";
	}
	return data;
}

int main(int argc, char **argv) {
	//Part 1 - handle command line options such as device selection, verbosity, etc.
	int platform_id = 0;
	int device_id = 0;

	for (int i = 1; i < argc; i++)	{
		if ((strcmp(argv[i], "-p") == 0) && (i < (argc - 1))) { platform_id = atoi(argv[++i]); }
		else if ((strcmp(argv[i], "-d") == 0) && (i < (argc - 1))) { device_id = atoi(argv[++i]); }
		else if (strcmp(argv[i], "-l") == 0) { std::cout << ListPlatformsDevices() << std::endl; }
		else if (strcmp(argv[i], "-h") == 0) { print_help(); return 0;}
	}

#pragma region Data Read+Setup

	//Type Definitions
	typedef int testType;
	typedef chrono::steady_clock::time_point TimePoint;
	typedef chrono::high_resolution_clock Clock;

	//Filename and path variables, needed for the ReadData() Function
	string filePath = "C:/Users/Student/Desktop/Temp/Assignment Item 1/CMP3110M_Assignment/";
	string fileName = "temp_lincolnshire_short.txt";
	filePath.append(fileName); //Append filename to directory path to get full file path

	//Time at which the performance timer clock started
	TimePoint perfTimerStart = Clock::now();	
	//Read the data file and save the data
	vector<int>* data = ReadData(filePath);
	//Stop the timer to get the readTime
	auto readTime = chrono::duration_cast<chrono::milliseconds>(Clock::now() - perfTimerStart).count();

	//Reset the Performance Timer (for usage for Total Run Speeds)
	perfTimerStart = Clock::now();

#pragma endregion

	//detect any potential exceptions
	try {
		//HOST OPERATIONS

		//SELECT COMPUTING DEVICES
		cl::Context context = GetContext(platform_id, device_id);
		//display the selected device
		std::cout << "Running on " << GetPlatformName(platform_id) << ", " << GetDeviceName(platform_id, device_id) << std::endl;
		//create a queue to which we will push commands for the device
		cl::CommandQueue queue(context, CL_QUEUE_PROFILING_ENABLE);

		//LOAD & BUILD DEVICE CODE
		cl::Program::Sources sources;
		AddSources(sources, "kernels.cl");
		cl::Program program(context, sources);
		//Build and debug the kernel code
		try {
			program.build();
		}
		catch (const cl::Error& err) {
			std::cout << "Build Status: " << program.getBuildInfo<CL_PROGRAM_BUILD_STATUS>(context.getInfo<CL_CONTEXT_DEVICES>()[0]) << std::endl;
			std::cout << "Build Options:\t" << program.getBuildInfo<CL_PROGRAM_BUILD_OPTIONS>(context.getInfo<CL_CONTEXT_DEVICES>()[0]) << std::endl;
			std::cout << "Build Log:\t " << program.getBuildInfo<CL_PROGRAM_BUILD_LOG>(context.getInfo<CL_CONTEXT_DEVICES>()[0]) << std::endl;
			throw err;
		}
			   		 
		//MEMORY ALLOCATION

		//Input (Host)
		//the following part adjusts the length of the input vector so it can be run for a specific workgroup size
		//if the total input length is divisible by the workgroup size
		//this makes the code more efficient
		size_t local_size = 1024;

		size_t padding_size = data->size() % local_size; //Get the padding_size based on the data size

		//if the input vector is not a multiple of the local_size
		//insert additional neutral elements (0 for addition) so that the total will not be affected
		if (padding_size) {
			//create an extra vector with neutral values
			vector<int> Data_ext(local_size - padding_size, 0);
			//append that extra vector to our input
			data->insert(data->end(), Data_ext.begin(), Data_ext.end());
		}

#pragma region Kernel Buffers Definition
		size_t input_elements = data->size(); // Number of input elements
		size_t input_size = data->size() * sizeof(testType); // Size in bytes
		size_t nr_groups = input_elements / local_size;

		//Output Vectors (Host)
		size_t output_size = input_elements * sizeof(testType); //Size in bytes

		vector<testType> B(input_elements);
		vector<testType> C(input_elements);
		//vector<testType> D(input_elements);
		//Due to add more
		//
		//

		//Buffers (Device)
		cl::Buffer buffer_A(context, CL_MEM_READ_ONLY, input_size); //Input Buffers = 1

		cl::Buffer buffer_B(context, CL_MEM_READ_WRITE, output_size); //Output Buffers = 2
		cl::Buffer buffer_C(context, CL_MEM_READ_WRITE, output_size);
		//cl::Buffer buffer_D(context, CL_MEM_READ_WRITE, output_size);
		//Due to add more
		//
		//

#pragma endregion

#pragma region Queue Kernel Buffers

		//Copy input array A to and initialise the other arrays to the device memory
		queue.enqueueWriteBuffer(buffer_A, CL_TRUE, 0, input_size, &(*data)[0]);

		// Zero buffer output on device memory
		queue.enqueueFillBuffer(buffer_B, 0, 0, output_size);
		queue.enqueueFillBuffer(buffer_C, 0, 0, output_size);
		//queue.enqueueFillBuffer(buffer_D, 0, 0, output_size);
		//Due to add more
		//
		//

#pragma endregion

#pragma region Kernel Creation and Setup

		// Setup and execute the device code (Kernels)
		cl::Kernel kernel_1 = cl::Kernel(program, "reduction_min"); //Find minimum kernel
		kernel_1.setArg(0, buffer_A);
		kernel_1.setArg(1, buffer_B);
		kernel_1.setArg(2, cl::Local(local_size * sizeof(testType)));//local memory size

		cl::Kernel kernel_2 = cl::Kernel(program, "reduction_max"); //Find maximum kernel
		kernel_2.setArg(0, buffer_A);
		kernel_2.setArg(1, buffer_C);
		kernel_2.setArg(2, cl::Local(local_size * sizeof(testType)));

		//Due to add more kernels
		//

		//
		//

#pragma endregion

		//PROFILING EVENTS
		// Create the profiling events that will measure the time each kernel takes to run
		// 1A & 2A are the Atomic versions min/max, which are profile_event 1 & 2 respectively
		cl::Event prof_event1;
		//cl::Event prof_event1A;
		cl::Event prof_event2;
		//cl::Event prof_event2A;
		//Due to add more profiling events
		//
		//

#pragma region Call Kernel

		// Call all the kernels in sequence - Except for the mean and standard deviation which require results from these to work
		queue.enqueueNDRangeKernel(kernel_1, cl::NullRange, cl::NDRange(input_elements), cl::NDRange(local_size), NULL, &prof_event1); //Minimum Kernel
		queue.enqueueNDRangeKernel(kernel_2, cl::NullRange, cl::NDRange(input_elements), cl::NDRange(local_size), NULL, &prof_event2); //Maximum Kernel
		//Due to add more to the queue
		//
		//

#pragma endregion

#pragma region Read Buffers + Kernel Output/Results

		//Read the Buffers by copying the results from the device(Kernels) to the host

		//Reduction Minimum
		queue.enqueueReadBuffer(buffer_B, CL_TRUE, 0, output_size, &B[0]);
		uint64_t p1 = prof_event1.getProfilingInfo<CL_PROFILING_COMMAND_END>() - prof_event1.getProfilingInfo<CL_PROFILING_COMMAND_START>();

		//Reduction Maximum
		queue.enqueueReadBuffer(buffer_C, CL_TRUE, 0, output_size, &C[0]);
		uint64_t p2 = prof_event2.getProfilingInfo<CL_PROFILING_COMMAND_END>() - prof_event2.getProfilingInfo<CL_PROFILING_COMMAND_START>();

		//Due to add more
		//
		//

		//KERNEL OUTPUT/RESULTS
		float minValue = (float)B[0] / 100.0f;
		float maxValue = (float)C[0] / 100.0f;
		//Due to add more results
		//
		//

		//Stop the timers and get the kernel run time and total run time
		auto runTime = chrono::duration_cast<std::chrono::milliseconds>(Clock::now() - perfTimerStart).count(); //Kernel Run Time
		auto totalTime = readTime + runTime; //Total Time = Read Time + Run Time
#pragma endregion
					   		 
#pragma region Output
		/*Input File Details*/
		cout << "\n---------------Input File Details---------------\n" << endl;

		cout << "Full File Path: " << filePath << endl;
		cout << "\nFile Name: " << fileName << endl;
		cout << "Total number of data values: " << (*data).size() << endl;
		cout << "Total time to read: " << (readTime / 1000.0f) << " seconds" << endl;
		cout << "Total time to run: " << (totalTime / 1000.0f) << " seconds" << endl;
		/*Results*/
		cout << "\n---------------Results---------------\n" << endl;

		//min (reduce + atomic?)
		cout << "Reduction Minimum Temperature = " << minValue << " | Execution Time [??]: " << p1 << endl;
		//max (reduce + atomic?)
		cout << "\nReduction Maximum Temperature = " << maxValue << " | Execution Time [??]: " << p2 << endl;

		//mean
		//median
		//1st quartile
		//3rd quartile

		//variance
		//std dev

		/*Profiling Data*/
		cout << "\n---------------Profiling Data---------------\n" << endl;

		//min (reduce + atomic?)
		cout << "Reduction Minimum  = " << GetFullProfilingInfo(prof_event1, ProfilingResolution::PROF_US) << endl;
		//max (reduce + atomic?)
		cout << "\nReduction Maximum  = " << GetFullProfilingInfo(prof_event2, ProfilingResolution::PROF_US) << endl;

		//mean
		//median
		//1st quartile
		//3rd quartile
		
		//variance
		//std dev

		cout << "\n" << endl;
#pragma endregion

	}
	catch (cl::Error err) {
		std::cerr << "ERROR: " << err.what() << ", " << getErrorString(err.err()) << std::endl;
	}


	//Prevent the program from exiting until the user presses a key
	cout << "To quit the program, press any key" << endl;
	cin.get();

	return 0;
}
