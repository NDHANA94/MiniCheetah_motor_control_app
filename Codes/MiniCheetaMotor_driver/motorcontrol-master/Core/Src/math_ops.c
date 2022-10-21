
#include "math_ops.h"
#include "lookup.h"


float fast_fmaxf(float x, float y){
    /// Returns maximum of x, y ///
    return (((x)>(y))?(x):(y));
    }

float fast_fminf(float x, float y){
    /// Returns minimum of x, y ///
    return (((x)<(y))?(x):(y));
    }

float fmaxf3(float x, float y, float z){
    /// Returns maximum of x, y, z ///
    return (x > y ? (x > z ? x : z) : (y > z ? y : z));
    }

float fminf3(float x, float y, float z){
    /// Returns minimum of x, y, z ///
    return (x < y ? (x < z ? x : z) : (y < z ? y : z));
    }
/*
float roundf(float x){
    /// Returns nearest integer ///
    return x < 0.0f ? ceilf(x - 0.5f) : floorf(x + 0.5f);
    }
  */
void limit_norm(float *x, float *y, float limit){
    /// Scales the lenght of vector (x, y) to be <= limit ///
    float norm = sqrtf(*x * *x + *y * *y);
    if(norm > limit){
        *x = *x * limit/norm;
        *y = *y * limit/norm;
        }
    }
    
void limit(float *x, float min, float max){
    *x = fast_fmaxf(fast_fminf(*x, max), min);
    }



float sin_lut(float theta){
	theta = fmodf(theta, TWO_PI_F);
	theta = theta<0 ? theta + TWO_PI_F : theta;

	return sin_tab[(int) (LUT_MULT*theta)];
}

float cos_lut(float theta){
	return sin_lut(PI_OVER_2_F - theta);
}
