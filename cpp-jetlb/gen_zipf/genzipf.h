//==================================================== file = genzipf.c =====
//=  Program to generate Zipf (power law) distributed random variables      =
//===========================================================================
//=  Notes: 1) Writes to a user specified output file                       =
//=         2) Generates user specified number of values                    =
//=         3) Run times is same as an empirical distribution generator     =
//=         4) Implements p(i) = C/i^alpha for i = 1 to N where C is the    =
//=            normalization constant (i.e., sum of p(i) = 1).              =
//=-------------------------------------------------------------------------=
//= Example user input:                                                     =
//=                                                                         =
//=   ---------------------------------------- genzipf.c -----              =
//=   -     Program to generate Zipf random variables        -              =
//=   --------------------------------------------------------              =
//=   Output file name ===================================> output.dat      =
//=   Random number seed =================================> 1               =
//=   Alpha vlaue ========================================> 1.0             =
//=   N value ============================================> 1000            =
//=   Number of values to generate =======================> 5               =
//=   --------------------------------------------------------              =
//=   -  Generating samples to file                          -              =
//=   --------------------------------------------------------              =
//=   --------------------------------------------------------              =
//=   -  Done!                                                              =
//=   --------------------------------------------------------              =
//=-------------------------------------------------------------------------=
//= Example output file ("output.dat" for above):                           =
//=                                                                         =
//=   1                                                                     =
//=   1                                                                     =
//=   161                                                                   =
//=   17                                                                    =
//=   30                                                                    =
//=-------------------------------------------------------------------------=
//=  Build: bcc32 genzipf.c                                                 =
//=-------------------------------------------------------------------------=
//=  Execute: genzipf                                                       =
//=-------------------------------------------------------------------------=
//=  Author: Kenneth J. Christensen                                         =
//=          University of South Florida                                    =
//=          WWW: http://www.csee.usf.edu/~christen                         =
//=          Email: christen@csee.usf.edu                                   =
//=-------------------------------------------------------------------------=
//=  History: KJC (11/16/03) - Genesis (from genexp.c)                      =
//===========================================================================
//----- Include files -------------------------------------------------------
#include <assert.h>             // Needed for assert() macro
#include <stdio.h>              // Needed for printf()
#include <stdlib.h>             // Needed for exit() and ato*()
#include <math.h>               // Needed for pow()

//----- Constants -----------------------------------------------------------
#define  FALSE          0       // Boolean false
#define  TRUE           1       // Boolean true

//----- Function prototypes -------------------------------------------------
int      zipf(double alpha, int n);  // Returns a Zipf random variable
double   rand_val(int seed);         // Jain's RNG

// A iterative binary search function. It returns 
// location of the first number that is not smaller than x
int binarySearch(double arr[], int l, int r, double x);

//===== Main program ========================================================
void genzipf(const char* file_name, unsigned int seed, float alpha, int n, unsigned int num_values)
{
	FILE   *fp;                   // File pointer to output file
	char   temp_string[256];      // Temporary string variable
	int    zipf_rv;               // Zipf random variable
	int    i;                     // Loop counter

	// Output banner
	printf("---------------------------------------- genzipf.c ----- \n");
	printf("-     Program to generate Zipf random variables        - \n");
	printf("-------------------------------------------------------- \n");

	// Prompt for output filename and then create/open the file
	#pragma warning(suppress : 4996)
	fp = fopen(file_name, "wb");
	if (fp == NULL)
	{
		printf("ERROR in creating output file (%s) \n", file_name);
		exit(1);
	}

	// Random number seed should be greater than 0
	rand_val(seed + 1);

	// Output "generating" message
	printf("-------------------------------------------------------- \n");
	printf("-  Generating samples to file                          - \n");
	printf("-------------------------------------------------------- \n");

	// Generate and output zipf random variables
	for (i = 0; i < num_values; i++)
	{
		zipf_rv = zipf(alpha, n);

		char flag = 0xFF;

		fwrite((const void*)& zipf_rv, sizeof(int), 1, fp);
		fwrite((const void*)& zipf_rv, sizeof(int), 1, fp);
		fwrite((const void*)& zipf_rv, sizeof(int), 1, fp);
		fwrite((const void*)& flag, sizeof(char), 1, fp);
		
		if (i % 1000000 == 0)
		{
			std::cout << "N: "<< i << " Alpha:" << alpha << std::endl;
		}
	}

	// Output "done" message and close the output file
	printf("-------------------------------------------------------- \n");
	printf("-  Done! \n");
	printf("-------------------------------------------------------- \n");
	fclose(fp);
}

//===========================================================================
//=  Function to generate Zipf (power law) distributed random variables     =
//=    - Input: alpha and N                                                 =
//=    - Output: Returns with Zipf distributed random variable              =
//===========================================================================
int zipf(double alpha, int n)
{
	static int first = TRUE;      // Static first time flag
	static double c = 0;          // Normalization constant
	double z;                     // Uniform random number (0 < z < 1)
	double sum_prob;              // Sum of probabilities
	double zipf_value;            // Computed exponential value to be returned
	int    i;                     // Loop counter

	static double* cdf = new double[n];

	// Compute normalization constant on first call only
	if (first == TRUE)
	{
		for (i = 1; i <= n; i++) 
		{
			c = c + (1.0 / pow((double)i, alpha));
		}			
		c = 1.0 / c;

		double c_prime = 0;
		cdf[0] = 0;		
		for (i = 1; i <= n; i++)
		{
			c_prime += (c / pow((double)i, alpha));
			cdf[i] = c_prime;
		}
		first = FALSE;
	}

	// Pull a uniform random number (0 < z < 1)
	do
	{
		z = rand_val(0);
	} while ((z == 0) || (z == 1));

	// Map z to the value
	int doubling_index = 1;
	while (cdf[doubling_index] < z)
	{
		doubling_index <<= 1;
	}


	zipf_value = binarySearch(cdf, (doubling_index >> 1) + 1, doubling_index, z);
	
	
	// Assert that zipf_value is between 1 and N
	assert((zipf_value >= 1) && (zipf_value <= n));

	return(zipf_value);
}

//=========================================================================
//= Multiplicative LCG for generating uniform(0.0, 1.0) random numbers    =
//=   - x_n = 7^5*x_(n-1)mod(2^31 - 1)                                    =
//=   - With x seeded to 1 the 10000th x value should be 1043618065       =
//=   - From R. Jain, "The Art of Computer Systems Performance Analysis," =
//=     John Wiley & Sons, 1991. (Page 443, Figure 26.2)                  =
//=========================================================================
double rand_val(int seed)
{
	const long  a = 16807;  // Multiplier
	const long  m = 2147483647;  // Modulus
	const long  q = 127773;  // m div a
	const long  r = 2836;  // m mod a
	static long x;               // Random int value
	long        x_div_q;         // x divided by q
	long        x_mod_q;         // x modulo q
	long        x_new;           // New x value

	// Set the seed if argument is non-zero and then return zero
	if (seed > 0)
	{
		x = seed;
		return(0.0);
	}

	// RNG using integer arithmetic
	x_div_q = x / q;
	x_mod_q = x % q;
	x_new = (a * x_mod_q) - (r * x_div_q);
	if (x_new > 0)
		x = x_new;
	else
		x = x_new + m;

	// Return a random value between 0.0 and 1.0
	return((double)x / m);
}

int binarySearch(double arr[], int l, int r, double x)
{
	while (l < r) {
		int m = l + (r - l) / 2;

		// If x greater, ignore left half 
		if (arr[m] < x)
			l = m + 1;

		// If x is smaller, ignore right half 
		else
			r = m;
	}

	return l;
}
