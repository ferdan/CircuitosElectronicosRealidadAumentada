EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Interface_Expansion:PCF8591 U1
U 1 1 61022479
P 6550 3350
F 0 "U1" H 6550 4331 50  0000 C CNN
F 1 "PCF8591" H 6550 4240 50  0000 C CNN
F 2 "" H 6550 3150 50  0001 C CNN
F 3 "http://www.nxp.com/documents/data_sheet/PCF8591.pdf" H 6550 3150 50  0001 C CNN
	1    6550 3350
	1    0    0    -1  
$EndComp
Wire Wire Line
	5950 3650 5850 3650
Wire Wire Line
	5850 3650 5850 3750
Wire Wire Line
	5950 3750 5850 3750
Connection ~ 5850 3750
Wire Wire Line
	5850 3750 5850 3850
Wire Wire Line
	5950 3850 5850 3850
$Comp
L MCU_Module:Arduino_UNO_R3 A1
U 1 1 61022485
P 4450 3600
F 0 "A1" H 4450 4781 50  0000 C CNN
F 1 "Arduino_UNO_R3" H 4450 4690 50  0000 C CNN
F 2 "Module:Arduino_UNO_R3" H 4450 3600 50  0001 C CIN
F 3 "https://www.arduino.cc/en/Main/arduinoBoardUno" H 4450 3600 50  0001 C CNN
	1    4450 3600
	1    0    0    -1  
$EndComp
$Comp
L Device:R R2
U 1 1 6102248B
P 5700 2750
F 0 "R2" H 5770 2796 50  0000 L CNN
F 1 "10k" H 5770 2705 50  0000 L CNN
F 2 "" V 5630 2750 50  0001 C CNN
F 3 "~" H 5700 2750 50  0001 C CNN
	1    5700 2750
	1    0    0    -1  
$EndComp
Wire Wire Line
	5850 4750 6550 4750
Connection ~ 6550 4750
Wire Wire Line
	5700 3350 5950 3350
$Comp
L Device:R R1
U 1 1 61022494
P 5350 2750
F 0 "R1" H 5420 2796 50  0000 L CNN
F 1 "10k" H 5420 2705 50  0000 L CNN
F 2 "" V 5280 2750 50  0001 C CNN
F 3 "~" H 5350 2750 50  0001 C CNN
	1    5350 2750
	1    0    0    -1  
$EndComp
Wire Wire Line
	6550 2550 5700 2550
Wire Wire Line
	5700 2550 5700 2600
Connection ~ 6550 2550
Wire Wire Line
	5700 2550 5350 2550
Wire Wire Line
	5350 2550 5350 2600
Connection ~ 5700 2550
Wire Wire Line
	4650 2600 4650 2550
Wire Wire Line
	4550 4700 4550 4750
Wire Wire Line
	5850 3850 5850 4750
Connection ~ 5850 3850
Wire Wire Line
	6550 4150 6550 4750
Wire Wire Line
	6550 4750 7200 4750
Wire Wire Line
	7150 3250 7200 3250
Wire Wire Line
	7150 3450 7200 3450
Wire Wire Line
	7200 3450 7200 3850
Wire Wire Line
	7150 3850 7200 3850
Connection ~ 7200 3850
Wire Wire Line
	7200 3850 7200 4750
Wire Wire Line
	4950 3600 5800 3600
Wire Wire Line
	7150 2950 7250 2950
Wire Wire Line
	7200 3250 7200 2550
Wire Wire Line
	7250 2950 7250 4200
Wire Wire Line
	5800 4200 7250 4200
Wire Wire Line
	5050 4100 4950 4100
Wire Wire Line
	4950 4000 5000 4000
Wire Wire Line
	5800 3600 5800 4200
Wire Wire Line
	5050 4100 5050 3050
Wire Wire Line
	5000 4000 5000 3000
Wire Wire Line
	5350 3450 5950 3450
Wire Wire Line
	5350 3000 5350 3450
Wire Wire Line
	5350 2900 5350 3000
Connection ~ 5350 3000
Wire Wire Line
	5000 3000 5350 3000
Wire Wire Line
	5700 2900 5700 3050
Wire Wire Line
	5700 3050 5700 3350
Connection ~ 5700 3050
Wire Wire Line
	5050 3050 5700 3050
Connection ~ 5350 2550
Wire Wire Line
	4650 2550 5350 2550
Connection ~ 5850 4750
Wire Wire Line
	4550 4750 5850 4750
Wire Wire Line
	6550 2550 7200 2550
$EndSCHEMATC
