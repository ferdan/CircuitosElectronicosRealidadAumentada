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
U 1 1 6100458C
P 5200 3650
F 0 "U1" H 5200 4631 50  0000 C CNN
F 1 "PCF8591" H 5200 4540 50  0000 C CNN
F 2 "" H 5200 3450 50  0001 C CNN
F 3 "http://www.nxp.com/documents/data_sheet/PCF8591.pdf" H 5200 3450 50  0001 C CNN
	1    5200 3650
	1    0    0    -1  
$EndComp
$Comp
L Transistor_FET:2N7000 Q1
U 1 1 61008D12
P 8950 4000
F 0 "Q1" H 9154 4046 50  0000 L CNN
F 1 "2N7000" H 9154 3955 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 9150 3925 50  0001 L CIN
F 3 "https://www.onsemi.com/pub/Collateral/NDS7002A-D.PDF" H 8950 4000 50  0001 L CNN
	1    8950 4000
	1    0    0    -1  
$EndComp
$Comp
L Interface_Expansion:PCF8591 U2
U 1 1 61003E9E
P 7450 3650
F 0 "U2" H 7450 4631 50  0000 C CNN
F 1 "PCF8591" H 7450 4540 50  0000 C CNN
F 2 "" H 7450 3450 50  0001 C CNN
F 3 "http://www.nxp.com/documents/data_sheet/PCF8591.pdf" H 7450 3450 50  0001 C CNN
	1    7450 3650
	1    0    0    -1  
$EndComp
Wire Wire Line
	4600 3950 4500 3950
Wire Wire Line
	4500 3950 4500 4050
Wire Wire Line
	4600 4050 4500 4050
Connection ~ 4500 4050
Wire Wire Line
	4500 4050 4500 4150
Wire Wire Line
	4600 4150 4500 4150
Wire Wire Line
	6850 4050 6750 4050
Wire Wire Line
	6750 4050 6750 4150
Wire Wire Line
	6850 4150 6750 4150
Wire Wire Line
	6850 3950 6750 3950
Wire Wire Line
	6750 3950 6750 2850
Connection ~ 6750 2850
$Comp
L MCU_Module:Arduino_UNO_R3 A1
U 1 1 61006DCE
P 3100 3900
F 0 "A1" H 3100 5081 50  0000 C CNN
F 1 "Arduino_UNO_R3" H 3100 4990 50  0000 C CNN
F 2 "Module:Arduino_UNO_R3" H 3100 3900 50  0001 C CIN
F 3 "https://www.arduino.cc/en/Main/arduinoBoardUno" H 3100 3900 50  0001 C CNN
	1    3100 3900
	1    0    0    -1  
$EndComp
$Comp
L Device:R R2
U 1 1 6101C398
P 4350 3050
F 0 "R2" H 4420 3096 50  0000 L CNN
F 1 "4.7k" H 4420 3005 50  0000 L CNN
F 2 "" V 4280 3050 50  0001 C CNN
F 3 "~" H 4350 3050 50  0001 C CNN
	1    4350 3050
	1    0    0    -1  
$EndComp
Wire Wire Line
	4500 5050 5200 5050
Connection ~ 5200 5050
Wire Wire Line
	4350 3650 4600 3650
$Comp
L Device:R R1
U 1 1 6101CC3D
P 4000 3050
F 0 "R1" H 4070 3096 50  0000 L CNN
F 1 "4.7k" H 4070 3005 50  0000 L CNN
F 2 "" V 3930 3050 50  0001 C CNN
F 3 "~" H 4000 3050 50  0001 C CNN
	1    4000 3050
	1    0    0    -1  
$EndComp
Wire Wire Line
	5200 2850 4350 2850
Wire Wire Line
	4350 2850 4350 2900
Connection ~ 5200 2850
Wire Wire Line
	4350 2850 4000 2850
Wire Wire Line
	4000 2850 4000 2900
Connection ~ 4350 2850
Wire Wire Line
	3300 2900 3300 2850
Connection ~ 4000 2850
Wire Wire Line
	4350 3200 4350 3300
Wire Wire Line
	4000 3200 4000 3300
Wire Wire Line
	4000 3750 4600 3750
Connection ~ 4500 5050
Wire Wire Line
	3200 5000 3200 5050
Wire Wire Line
	4500 4150 4500 5050
Connection ~ 4500 4150
Wire Wire Line
	5200 4450 5200 5050
Wire Wire Line
	6750 4150 6750 5050
Connection ~ 6750 4150
Wire Wire Line
	7450 4450 7450 5050
Wire Wire Line
	3200 5050 4500 5050
Wire Wire Line
	3300 2850 4000 2850
$Comp
L Device:R R5
U 1 1 61038667
P 9050 3500
F 0 "R5" V 8843 3500 50  0000 C CNN
F 1 "2.2k" V 8934 3500 50  0000 C CNN
F 2 "" V 8980 3500 50  0001 C CNN
F 3 "~" H 9050 3500 50  0001 C CNN
	1    9050 3500
	1    0    0    -1  
$EndComp
Wire Wire Line
	3850 3300 4000 3300
Connection ~ 4000 3300
Wire Wire Line
	4000 3300 4000 3750
Wire Wire Line
	4250 3300 4350 3300
Connection ~ 4350 3300
Wire Wire Line
	4350 3300 4350 3650
Wire Wire Line
	3850 2600 3850 3300
Wire Wire Line
	9050 3250 9050 3350
Wire Wire Line
	9050 4200 9050 5050
Wire Wire Line
	9050 3650 9050 3750
Wire Wire Line
	6750 2850 7450 2850
Connection ~ 7450 2850
Wire Wire Line
	7450 2850 8100 2850
Connection ~ 6750 5050
Connection ~ 7450 5050
Wire Wire Line
	6750 5050 7450 5050
Wire Wire Line
	8050 3250 8600 3250
Wire Wire Line
	4250 2550 6400 2550
Wire Wire Line
	3850 2600 6050 2600
Wire Wire Line
	8700 4000 8750 4000
Wire Wire Line
	5200 2850 5850 2850
Wire Wire Line
	5200 5050 5850 5050
Wire Wire Line
	7450 5050 8100 5050
Wire Wire Line
	5800 3550 5850 3550
Connection ~ 5850 2850
Wire Wire Line
	8100 3550 8100 2850
Wire Wire Line
	8100 3550 8050 3550
Wire Wire Line
	5800 3750 5850 3750
Wire Wire Line
	5850 3750 5850 4150
Connection ~ 5850 5050
Wire Wire Line
	5850 5050 6750 5050
Wire Wire Line
	5800 4150 5850 4150
Connection ~ 5850 4150
Wire Wire Line
	5850 4150 5850 5050
Wire Wire Line
	8050 3750 8100 3750
Wire Wire Line
	8100 3750 8100 4150
Connection ~ 8100 5050
Wire Wire Line
	8100 5050 9050 5050
Wire Wire Line
	8050 4150 8100 4150
Connection ~ 8100 4150
Wire Wire Line
	8100 4150 8100 5050
Wire Wire Line
	3600 3900 4450 3900
Connection ~ 8600 3250
Wire Wire Line
	8600 3250 9050 3250
Wire Wire Line
	8550 4650 8550 3750
Wire Wire Line
	8550 3750 9050 3750
Connection ~ 9050 3750
Wire Wire Line
	9050 3750 9050 3800
Wire Wire Line
	5800 3250 5900 3250
Wire Wire Line
	5850 3550 5850 2850
Wire Wire Line
	3600 4000 4400 4000
Wire Wire Line
	3600 4100 4350 4100
Wire Wire Line
	8600 3250 8600 4600
Wire Wire Line
	8700 4500 5900 4500
Wire Wire Line
	5900 3250 5900 4500
Wire Wire Line
	4450 3900 4450 4500
Wire Wire Line
	4450 4500 5900 4500
Connection ~ 5900 4500
Wire Wire Line
	4400 4000 4400 4550
Wire Wire Line
	4400 4550 8500 4550
Wire Wire Line
	8500 4550 8500 4000
Wire Wire Line
	8500 4000 8700 4000
Connection ~ 8700 4000
Wire Wire Line
	4350 4100 4350 4600
Wire Wire Line
	4350 4600 8600 4600
Wire Wire Line
	3600 4200 4300 4200
Wire Wire Line
	4300 4200 4300 4650
Wire Wire Line
	4300 4650 8550 4650
Wire Wire Line
	8700 4000 8700 4500
Wire Wire Line
	4250 2550 4250 3300
Wire Wire Line
	3700 4400 3600 4400
Wire Wire Line
	3700 2550 4250 2550
Connection ~ 4250 2550
Wire Wire Line
	3700 2550 3700 4400
Wire Wire Line
	3600 4300 3650 4300
Wire Wire Line
	3650 4300 3650 2600
Wire Wire Line
	3650 2600 3850 2600
Connection ~ 3850 2600
Wire Wire Line
	5850 2850 6750 2850
Wire Wire Line
	6400 3650 6850 3650
Wire Wire Line
	6400 2550 6400 3650
Wire Wire Line
	6050 2600 6050 3750
Wire Wire Line
	6050 3750 6850 3750
$EndSCHEMATC
