/*
 * math_ops.c
 *
 *  Created on: Oct 13, 2022
 *      Author: Nipun Dhananjaya Weerakkodi
 */

#include "math_ops.h"


float fmaxf(float x, float y){
	// return maximum of x, y //
	return (((x)>(y)) ? (x) : (y));
}

float fminf(float x, float y){
	// return minimum of x, y //
	return (((x)<(y)) ? (x) : (y));
}

float fmaxf3(float x, float y, float z){
	// return maximum of x, y //
	return (x > y ? ( x > z ? x : z) : ( y > z ? y : z));
}

float fminf3(float x, float y, float z){
	// return minimum of x, y //
	return (x < y ? ( x < z ? x : z) : ( y < z ? y : z));
}


void limit_norm(float *x, float *y, float limit){
	//scale the length of vector (x,y) to be <= limit //
	float norm = sqrt(*x * *x + *y * *y);
	if (norm > limit){
		*x = *x * limit/norm;
		*y = *y * limit/norm;
	}
}

int float_to_uint(float x, float x_min, float x_max, int bits){
    /// Converts a float to an unsigned int, given range and number of bits ///
    float span = x_max - x_min;
    float offset = x_min;
    return (int) ((x-offset)*((float)((1<<bits)-1))/span);
}


float uint_to_float(int x_int, float x_min, float x_max, int bits){
    /// converts unsigned int to float, given range and number of bits ///
    float span = x_max - x_min;
    float offset = x_min;
    return ((float)x_int)*span/((float)((1<<bits)-1)) + offset;
}
