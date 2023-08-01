/*
 * math_ops.h
 *
 *  Created on: Oct 13, 2022
 *      Author: nd94
 */

#ifndef INC_MATH_OPS_H_
#define INC_MATH_OPS_H_

#include "math.h"


float fmaxf(float x, float y);
float fminf(float x, float y);
float fmaxf3(float x, float y, float z);
float fminf3(float x, float y, float z);
void  limit_norm(float *x, float *y, float limit);

int float_to_uint(float x, float x_min, float x_max, int bits);
float uint_to_float(int x_int, float x_min, float x_max, int bits);

#endif /* INC_MATH_OPS_H_ */
