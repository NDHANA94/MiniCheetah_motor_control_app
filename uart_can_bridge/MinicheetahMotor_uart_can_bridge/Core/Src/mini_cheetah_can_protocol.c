/*
 * mini_cheetah_can_protocol.c
 *
 *  Created on: Oct 12, 2022
 *      Author: Nipun Dhananjaya Weerakkodi
 */


#include "mini_cheetah_can_protocol.h"

// CAN_rx_msg can_rx_msg;
// CAN_tx_msg can_tx_msg;





// void can_rx_init(){
// 	can_rx_msg.can_filter.FilterFIFOAssignment=CAN_FILTER_FIFO0; 	// set fifo assignment
// 	can_rx_msg.can_filter.FilterIdHigh=12<<5; 				// CAN ID
// 	can_rx_msg.can_filter.FilterIdLow=0x0;
// 	can_rx_msg.can_filter.FilterMaskIdHigh=0;
// 	can_rx_msg.can_filter.FilterMaskIdLow=0;
// 	can_rx_msg.can_filter.FilterMode = CAN_FILTERMODE_IDMASK;
// 	can_rx_msg.can_filter.FilterScale=CAN_FILTERSCALE_32BIT;
// 	can_rx_msg.can_filter.FilterActivation=ENABLE;
// 	HAL_CAN_ConfigFilter(&hcan, &can_rx_msg.can_filter);
// }

// void can_tx_init(){
// 	can_tx_msg.tx_header.DLC = 8; 			// message size of 8 byte
// 	can_tx_msg.tx_header.IDE=CAN_ID_STD; 		// set identifier to standard
// 	can_tx_msg.tx_header.RTR=CAN_RTR_DATA; 	// set data type to remote transmission request?
// }



void pack_cmd(uint8_t id)
{
	/// CAN Command Packet Structure ///
	/// 16 bit position command, between -4*pi and 4*pi
	/// 12 bit velocity command, between -30 and + 30 rad/s
	/// 12 bit kp, between 0 and 500 N-m/rad
	/// 12 bit kd, between 0 and 100 N-m*s/rad
	/// 12 bit feed forward torque, between -18 and 18 N-m
	/// CAN Packet is 8 8-bit words
	/// Formatted as follows.  For each quantity, bit 0 is LSB
	/// 0: [position[15-8]]
	/// 1: [position[7-0]]
	/// 2: [velocity[11-4]]
	/// 3: [velocity[3-0], kp[11-8]]
	/// 4: [kp[7-0]]
	/// 5: [kd[11-4]]
	/// 6: [kd[3-0], torque[11-8]]
	/// 7: [torque[7-0]]

	// limit data to be within bounds //
	motor-> cmd.p_des 	= fminf(fmaxf(P_MIN, motor->cmd.p_des), P_MAX);
	motor->cmd.v_des 	= fminf(fmaxf(V_MIN, motor->cmd.v_des), V_MAX);
	motor->cmd.kp 		= fminf(fmaxf(KP_MIN, motor->cmd.kp), KP_MAX);
	motor->cmd.kd 		= fminf(fmaxf(KD_MIN, motor->cmd.kd), KD_MAX);
	motor->cmd.trq 		= fminf(fmaxf(-I_MAX, motor->cmd.trq), I_MAX);
	// convert floats to unsigned ints //
	int p_int	= float_to_uint(motor->cmd.p_des, P_MIN, P_MAX, 16);
	int v_int 	= float_to_uint(motor->cmd.v_des, V_MIN, V_MAX, 12);
	int kp_int 	= float_to_uint(motor->cmd.kp, KP_MIN, KP_MAX, 12);
	int kd_int 	= float_to_uint(motor->cmd.kd, KD_MIN, KD_MAX, 12);
	int t_int 	= float_to_uint(motor->cmd.trq, -I_MAX, I_MAX, 12);

	motor[id-1].tx_data[0] = p_int>>8;
	motor[id-1].tx_data[1] = p_int&0xFF;
	motor[id-1].tx_data[2] = v_int>>4;
	motor[id-1].tx_data[3] = ((v_int&0xF)<<4) | (kp_int>>8);
	motor[id-1].tx_data[4] = kp_int&0xFF;
	motor[id-1].tx_data[5] = kd_int>>4;
	motor[id-1].tx_data[6] = ((kd_int&0xF)<<4) | (t_int>>8);
	motor[id-1].tx_data[7] = t_int&0xFF;

}


void set_motor_cmd(uint8_t id, float p_des, float v_des, float kp, float kd, float trq){
	motor[id-1].cmd.p_des = p_des;
	motor[id-1].cmd.v_des = v_des;
	motor[id-1].cmd.kp = kp;
	motor[id-1].cmd.kd = kd;
	motor[id-1].cmd.trq = trq;
	pack_cmd(id);
}

void sendCmd2Motor(uint8_t id){
	//char msg[50];
	// set StdId in TxHeader
	can_tx_msg.tx_header.StdId = id;
	// set can_tx_msg.tx_data
	for (int i = 0; i < can_tx_msg.tx_header.DLC; i++){
		can_tx_msg.tx_data[i] = motor[id-1].tx_data[i];
	}
	// Send can message
	if (HAL_CAN_AddTxMessage(&hcan, &can_tx_msg.tx_header, can_tx_msg.tx_data, &can_tx_msg.TxMailbox) != HAL_OK)
		{
			can_tx_msg.isSent = false;
			HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
			//sprintf(msg, "Error: sending CAN message to Motor %d \n\r", id);
			//HAL_UART_Transmit(&huart1, (uint8_t*)msg, strlen(msg), HAL_MAX_DELAY);
			Error_Handler();
		}

	can_tx_msg.isSent = true;

	//sprintf(msg, "sending CAN message to Motor %d.. \n\r", id);
	//HAL_UART_Transmit(&huart1, (uint8_t*)msg, strlen(msg), HAL_MAX_DELAY);
}


void unpack_reply()
{
	/// CAN Reply Packet Structure ///
	/// 16 bit position, between -4*pi and 4*pi
	/// 12 bit velocity, between -30 and + 30 rad/s
	/// 12 bit current, between -40 and 40;
	/// CAN Packet is 5 8-bit words
	/// Formatted as follows.  For each quantity, bit 0 is LSB
	/// 0: [position[15-8]]
	/// 1: [position[7-0]]
	/// 2: [velocity[11-4]]
	/// 3: [velocity[3-0], current[11-8]]
	/// 4: [current[7-0]]

	// unpack ints from can buffer
	int id = can_rx_msg.rx_data[0];
	int p_f = (can_rx_msg.rx_data[1]<<8) | can_rx_msg.rx_data[2];
	int v_f = (can_rx_msg.rx_data[3]<<4) | (can_rx_msg.rx_data[4]>>4);
	int t_f = ((can_rx_msg.rx_data[4]&0xF)<<8) | can_rx_msg.rx_data[5];

	// convert unsigned ints to float
	float p = uint_to_float(p_f, P_MIN, P_MAX, 16);
	float v = uint_to_float(v_f, V_MIN, V_MAX, 12);
	float t = uint_to_float(t_f, -I_MAX, I_MAX, 12);

	// set motor state
	motor[id-1].cur_state.p_cur = p;
	motor[id-1].cur_state.v_cur = v;
	motor[id-1].cur_state.t_cur = t;


}

void enable_motor(Motor *motor)
{
	char msg[20];
	uint8_t tx_can[8];
	for(int i = 0; i<7; i++){
		tx_can[i] = 0xFF;
	}
	tx_can[7] = 0xFC;

	can_tx_msg.tx_header.StdId = motor->id;
	if (HAL_CAN_AddTxMessage(&hcan, &can_tx_msg.tx_header, tx_can, &can_tx_msg.TxMailbox) != HAL_OK)
	{
		HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
		//sprintf(msg, "Motor %d enable CAN message Error!\n\r", motor->id);
		//HAL_UART_Transmit_DMA(&huart1, (uint8_t*)msg, strlen(msg));
		Error_Handler();
	}
	//sprintf(msg, "Motor %d enable cmd sent!\n\r", motor->id);
	//HAL_UART_Transmit_DMA(&huart1, (uint8_t*)msg, strlen(msg));

}

void disable_motor(Motor *motor)
{
	char msg[20];
	uint8_t tx_can[8];
	for(int i = 0; i<7; i++){
		tx_can[i] = 0xFF;
	}
	tx_can[7] = 0xFD;
	can_tx_msg.tx_header.StdId = motor->id;
	if (HAL_CAN_AddTxMessage(&hcan, &can_tx_msg.tx_header, tx_can, &can_tx_msg.TxMailbox) != HAL_OK)
	{
		HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
		//sprintf(msg, "Motor %u disable CAN message Error!\n\r", motor->id);
		//HAL_UART_Transmit(&huart1, (uint8_t*)msg, strlen(msg), HAL_MAX_DELAY);
		Error_Handler();
	}
	//sprintf(msg, "Motor %d disable cmd sent!\n\r", motor->id);
	//HAL_UART_Transmit_DMA(&huart1, (uint8_t*)msg, strlen(msg));

}


