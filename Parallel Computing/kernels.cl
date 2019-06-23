///////////////////////////////////////
//CMP3103M - Parallel Computing////////
//Assignment Item 1 - Weather Summary//
//JOS13502565 - Nathaniel Josephs//////
//kernels.cl///////////////////////////
///////////////////////////////////////

//a simple OpenCL kernel which adds two vectors A and B together into a third vector C
kernel void add(global const int* A, global const int* B, global int* C) {
	int id = get_global_id(0);
	C[id] = A[id] + B[id];
}

//a simple smoothing kernel averaging values in a local window (radius 1)
kernel void avg_filter(global const int* A, global int* B) {
	int id = get_global_id(0);
	B[id] = (A[id - 1] + A[id] + A[id + 1])/3;
}

//a simple 2D kernel
kernel void add2D(global const int* A, global const int* B, global int* C) {
	int x = get_global_id(0);
	int y = get_global_id(1);
	int width = get_global_size(0);
	int height = get_global_size(1);
	int id = x + y*width;

	printf("id = %d x = %d y = %d w = %d h = %d\n", id, x, y, width, height);

	C[id]= A[id]+ B[id];
}

//ADD/SUM KERNEL USED FOR MEAN TEMPERATURE

/*Kernel that uses a reduction pattern to find the minimum value in the input vector (A)
This is done by comparing two values from the vector and storing the smallest of the two.
This will repeat until the overall smallest value is stored in the first index position of the returned
vector (B).*/
kernel void reduction_min(global const int* A, global int* B, local int* scratch)
{
	int id = get_global_id(0);
	int lid = get_local_id(0);
	int N = get_local_size(0); //N = work group size

	//put all(N) values from global memory into local memory
	scratch[lid] = A[id];

	//Await threads: for the global memory to be copied to the local memory
	barrier(CLK_LOCAL_MEM_FENCE);

	for (int i = 1; i < N; i *= 2)
	{
		if (!(lid % (i * 2)) && ((lid + i) < N))
		{
			scratch[lid] = (scratch[lid] < scratch[lid + i]) ? scratch[lid] : scratch[lid + i];
		}

		//Await threads: for the global memory to be copied to the local memory
		barrier(CLK_LOCAL_MEM_FENCE);
	}

	//Add results from local work groups to the first array element
	//This is a serial operation
	//Copy the local 'cache' to the output array
	if (!lid) {
		atomic_min(&B[0], scratch[lid]);
	}
}

/*Kernel that uses a reduction pattern to find the maximum value in the input vector (A)
This is done by comparing two values from the vector and storing the largest of the two.
This will repeat until the overall largest value is stored in the first index position of the returned
vector (B). ESSENTIALLY THE SAME BUT FLIPPED*/
kernel void reduction_max(global const int* A, global int* B, local int* scratch)
{
	int id = get_global_id(0);
	int lid = get_local_id(0);
	int N = get_local_size(0); //N = work group size

	//put all(N) values from global memory into local memory
	scratch[lid] = A[id];

	//Await threads: for the global memory to be copied to the local memory
	barrier(CLK_LOCAL_MEM_FENCE);

	for (int i = 1; i < N; i *= 2)
	{
		if (!(lid % (i * 2)) && ((lid + i) < N))
		{
			scratch[lid] = (scratch[lid] > scratch[lid + i]) ? scratch[lid] : scratch[lid + i];
		}

		//Await threads: for the global memory to be copied to the local memory
		barrier(CLK_LOCAL_MEM_FENCE);
	}

	//Add results from local work groups to the first array element
	//This is a serial operation
	//Copy the local 'cache' to the output array
	if (!lid) {
		atomic_max(&B[0], scratch[lid]);
	}
}

//ATMOIC MIN AND MAX KERNELS?????

//SORT KERNEL USED FOR MEDIAN AND PERCENTILES