/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    usart.h
  * @brief   This file contains all the function prototypes for
  *          the usart.c file
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
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __USART_H__
#define __USART_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* USER CODE BEGIN Includes */
// #include "mini_cheetah_can_protocol.h"
#include "can.h"
#include "math_ops.h"
#define UART1_RX_BUFFER_SIZE 9
#define UART1_TX_BUFFER_SIZE 2
/* USER CODE END Includes */

extern UART_HandleTypeDef huart1;

/* USER CODE BEGIN Private defines */
extern uint8_t uart1_rxBuf[UART1_RX_BUFFER_SIZE];
extern uint8_t* uart1_txBuf;

/* USER CODE END Private defines */

void MX_USART1_UART_Init(void);

/* USER CODE BEGIN Prototypes */
void Start_uart1_rx_DMA(void);
// void Start_uart1_tx_DMA(void);
extern void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart);
extern void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart);
/* USER CODE END Prototypes */

#ifdef __cplusplus
}
#endif

#endif /* __USART_H__ */

