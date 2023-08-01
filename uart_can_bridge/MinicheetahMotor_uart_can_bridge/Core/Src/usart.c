/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    usart.c
  * @brief   This file provides code for the configuration
  *          of the USART instances.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "usart.h"

/* USER CODE BEGIN 0 */
uint8_t uart1_rxBuf[UART1_RX_BUFFER_SIZE];
uint8_t* uart1_txBuf;
/* USER CODE END 0 */

UART_HandleTypeDef huart1;
DMA_HandleTypeDef hdma_usart1_tx;
DMA_HandleTypeDef hdma_usart1_rx;

/* USART1 init function */

void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

void HAL_UART_MspInit(UART_HandleTypeDef* uartHandle)
{

  GPIO_InitTypeDef GPIO_InitStruct = {0};
  if(uartHandle->Instance==USART1)
  {
  /* USER CODE BEGIN USART1_MspInit 0 */

  /* USER CODE END USART1_MspInit 0 */
    /* USART1 clock enable */
    __HAL_RCC_USART1_CLK_ENABLE();

    __HAL_RCC_GPIOA_CLK_ENABLE();
    /**USART1 GPIO Configuration
    PA9     ------> USART1_TX
    PA10     ------> USART1_RX
    */
    GPIO_InitStruct.Pin = GPIO_PIN_9;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    GPIO_InitStruct.Pin = GPIO_PIN_10;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /* USART1 DMA Init */
    /* USART1_TX Init */
    hdma_usart1_tx.Instance = DMA1_Channel4;
    hdma_usart1_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
    hdma_usart1_tx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_usart1_tx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_usart1_tx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
    hdma_usart1_tx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
    hdma_usart1_tx.Init.Mode = DMA_NORMAL;
    hdma_usart1_tx.Init.Priority = DMA_PRIORITY_MEDIUM;
    if (HAL_DMA_Init(&hdma_usart1_tx) != HAL_OK)
    {
      Error_Handler();
    }

    __HAL_LINKDMA(uartHandle,hdmatx,hdma_usart1_tx);

    /* USART1_RX Init */
    hdma_usart1_rx.Instance = DMA1_Channel5;
    hdma_usart1_rx.Init.Direction = DMA_PERIPH_TO_MEMORY;
    hdma_usart1_rx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_usart1_rx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_usart1_rx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
    hdma_usart1_rx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
    hdma_usart1_rx.Init.Mode = DMA_NORMAL;
    hdma_usart1_rx.Init.Priority = DMA_PRIORITY_HIGH;
    if (HAL_DMA_Init(&hdma_usart1_rx) != HAL_OK)
    {
      Error_Handler();
    }

    __HAL_LINKDMA(uartHandle,hdmarx,hdma_usart1_rx);

    /* USART1 interrupt Init */
    HAL_NVIC_SetPriority(USART1_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(USART1_IRQn);
  /* USER CODE BEGIN USART1_MspInit 1 */

  /* USER CODE END USART1_MspInit 1 */
  }
}

void HAL_UART_MspDeInit(UART_HandleTypeDef* uartHandle)
{

  if(uartHandle->Instance==USART1)
  {
  /* USER CODE BEGIN USART1_MspDeInit 0 */

  /* USER CODE END USART1_MspDeInit 0 */
    /* Peripheral clock disable */
    __HAL_RCC_USART1_CLK_DISABLE();

    /**USART1 GPIO Configuration
    PA9     ------> USART1_TX
    PA10     ------> USART1_RX
    */
    HAL_GPIO_DeInit(GPIOA, GPIO_PIN_9|GPIO_PIN_10);

    /* USART1 DMA DeInit */
    HAL_DMA_DeInit(uartHandle->hdmatx);
    HAL_DMA_DeInit(uartHandle->hdmarx);

    /* USART1 interrupt Deinit */
    HAL_NVIC_DisableIRQ(USART1_IRQn);
  /* USER CODE BEGIN USART1_MspDeInit 1 */

  /* USER CODE END USART1_MspDeInit 1 */
  }
}

/* =============================== USER CODE BEGIN 1 ======================================= */

// void execute_rx_cmd(void)
// {
// 	//[0] id
// 	//[1] p_h
// 	//[2] p_l
// 	//[3] v_h(8)
// 	//[4] v_l(4) | kp_h(4)
// 	//[5] kp_l[8]
// 	//[6] kd_h[8]
// 	//[7] kd_l[4] | i_h[4]
// 	//[8] i_l[8]
// 	int id = uart1_rxBuf[0];
// 	// if motor enable command
// 	if (uart1_rxBuf[1] == 0xFF && uart1_rxBuf[2] == 0xFF && uart1_rxBuf[3] == 0xFF && uart1_rxBuf[4] == 0xFF\
// 		&& uart1_rxBuf[5] == 0xFF && uart1_rxBuf[6] == 0xFF && uart1_rxBuf[7] == 0xFF && uart1_rxBuf[8] == 0xFC){
// 		enable_motor(&motor[id-1]);
// 	}
// 	// if motor disable command
// 	else if (uart1_rxBuf[1] == 0xFF && uart1_rxBuf[2] == 0xFF && uart1_rxBuf[3] == 0xFF && uart1_rxBuf[4] == 0xFF\
// 			&& uart1_rxBuf[5] == 0xFF && uart1_rxBuf[6] == 0xFF && uart1_rxBuf[7] == 0xFF && uart1_rxBuf[8] == 0xFD){
// 			disable_motor(&motor[id-1]);
// 	}
// 	// if other command
// 	else{
// 		for (int i = 0; i < 8; i++){
// 			motor[id-1].tx_data[i] = uart1_rxBuf[i+1];
// 		}
// 		sendCmd2Motor(id);
// 		// unpack
// 		float p = (uart1_rxBuf[1]<<8) | uart1_rxBuf[2];
// 		float v = (uart1_rxBuf[3]<<4) | uart1_rxBuf[4]>>4;
// 		float kp = (uart1_rxBuf[4]&0xF)<<8 | uart1_rxBuf[5];
// 		float kd = uart1_rxBuf[6]<<4 | uart1_rxBuf[7]>>4;
// 		float i = (uart1_rxBuf[7]&0xF)<<8 | uart1_rxBuf[8];
// 		// uint to float
// 		p = uint_to_float(p, P_MIN, P_MAX, 16);
// 		v = uint_to_float(v, V_MIN, V_MAX, 12);
// 		kp = uint_to_float(kp, KP_MIN, KP_MAX, 12);
// 		kd = uint_to_float(kd, KD_MIN, KD_MAX, 12);
// 		i = uint_to_float(i, -I_MAX, I_MAX, 12);
// 		// set motor command
// 		motor[id-1].cmd.p_des = p;
// 		motor[id-1].cmd.v_des = v;
// 		motor[id-1].cmd.kp = kp;
// 		motor[id-1].cmd.kd = kd;
// 		motor[id-1].cmd.trq = i;

// 	}



// }



void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	if (huart->Instance == USART1)
	{
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
    tx_canHeader.StdId = uart1_rxBuf[0];
    for (int i = 0; i<8; i++){
      can_tx_data[i] = uart1_rxBuf[i+1];
    }
    if (HAL_CAN_AddTxMessage(&hcan, &tx_canHeader, can_tx_data, &TxMailbox) != HAL_OK)
    {
      Error_Handler();
    }
		// execute_rx_cmd();
    // HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
	}

	HAL_UART_Receive_DMA(&huart1, uart1_rxBuf, UART1_RX_BUFFER_SIZE);
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart)
{
	if (huart->Instance == USART1)
	{
		HAL_UART_Transmit_DMA(&huart1, can_rx_data, 6);
	}
}


void Start_uart1_rx_DMA(void)
{
	HAL_UART_Receive_DMA(&huart1, uart1_rxBuf, UART1_RX_BUFFER_SIZE);
}


void Start_uart1_tx_DMA(void)
{
	char msg[50];
	sprintf(msg, "HELLO\n\r");
  //sprintf(msg, "id: %d \t pos: %f \t vel: %f \t I: %f \n\t", motor[0].id, motor[0].cur_state.p_cur, motor[0].cur_state.v_cur, motor[0].cur_state.t_cur);
	HAL_UART_Transmit_DMA(&huart1, msg, strlen(msg));
}


/* ====================================== USER CODE END 1 =================================================== */
