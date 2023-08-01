/*
 * mini_cheetah_can_protocol.h
 *
 *  Created on: Oct 12, 2022
 *      Author: nd94
 */

#ifndef INC_MINI_CHEETAH_CAN_PROTOCOL_H_
#define INC_MINI_CHEETAH_CAN_PROTOCOL_H_

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "can.h"
#include "usart.h"
#include "math_ops.h"
#include "stdbool.h"

#define NUM_OF_MOTORS 1

#define P_MIN 		-12.5f 		//radians
#define P_MAX 		 12.5f
#define V_MIN		-65.0f 		// rad/s
#define V_MAX		 65.0f
#define GR			 1.0f
#define KT			 1.0f
#define KP_MIN		 0.0f 		// N-m/rad
#define KP_MAX		 500.0f
#define KD_MIN		 0.0f		// N-m/rad/s
#define KD_MAX		 5.0f
#define I_MAX 		 40.0f

typedef struct{
	CAN_RxHeaderTypeDef 	rx_header;
	CAN_FilterTypeDef 		can_filter;
	uint8_t 				rx_data[6];
}CAN_rx_msg;

typedef struct{
	uint32_t 		 		TxMailbox;
	CAN_TxHeaderTypeDef 	tx_header;
	uint8_t 				tx_data[8];
	bool 					isSent;
}CAN_tx_msg;

typedef struct{
	float p_des, v_des, kp, kd, trq; //position
}COMMANDS;

typedef struct{
	float p_cur, v_cur, t_cur;
}MotorState;

typedef struct{
	uint8_t 		id;
	COMMANDS 		cmd;
	MotorState 		cur_state;
	uint8_t 		tx_data[8];
	char ERROR[];
}Motor;

extern CAN_rx_msg can_rx_msg;
extern CAN_tx_msg can_tx_msg;
extern Motor motor[NUM_OF_MOTORS];

// void can_rx_init();
// void can_tx_init();
//void pack_cmd(uint8_t id);
// void set_motor_cmd(uint8_t id, float p_des, float v_des, float kp, float kd, float trq);
// void sendCmd2Motor(uint8_t id);
// void unpack_reply();
// void enable_motor(Motor *motor);
// void disable_motor(Motor *motor);

#ifdef __cplusplus
}
#endif

#endif /* INC_MINI_CHEETAH_CAN_PROTOCOL_H_ */
