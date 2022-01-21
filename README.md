# Y86-64+ 시뮬레이터
## 개요
대학교 학부 과정 중 컴퓨터 구조 수업 시간에 사용되는 Y86-64( http://csapp.cs.cmu.edu/ )의 개선버전.
오리지널 버전의 Y86-64에 일부 명령어를 새롭게 추가한 후 파이썬으로 재구성하여 제작됨.

## 시뮬레이터 구성
### 어셈블리어 파일 및 목적 파일
어셈블리어 파일은 오리지널 버전에서 일부 명령어가 추가 되었기 때문에 .yps라는 확장자를 사용하는 것을 원칙으로 함.
그러나 기존 Y86-64 코드의 명령어 중 매크로 명령어 한 개를 제외하면 모두 사용할 수 있기 때문에 .ys라는 확장자도 사용할 수 있음.

목적 파일은 텍스트 기반으로 메모리 위치와 기계어 코드, 어셈블리어 코드가 같이 나열된 오리지널 버전과는 달리 순수 바이너리 코드로만 구성되어 있기 때문에
.ypo 또는 .ybin이라는 확장자만을 사용함.

### 어셈블러와 역 어셈블러
어셈블러는 어셈블리어 파일을 입력으로 하여 바이너리 코드로 구성된 목적 파일을 출력함.

목적 파일이 순수 바이너리 코드로만 구성되어 있기 때문에 별도로 역 어셈블러가 존재함.
바이너리 파일에서 변환하기 때문에 레이블은 남지 않으며 정수 또한 16진수로 된 부호 없는 정수로 표현됨.

### 시뮬레이터
시뮬레이터는 TK와 LTK를 사용하여 GUI 구성한 오리지널 버전과는 달리 gdbgui와 같이 시뮬레이터는 하나의 웹 서버로 동작하고 웹 브라우저에서 조작하는 형태로 동작됨.
웹 서버 엔진은 파이썬의 소켓을 이용하여 자체 제작한 모듈을 사용하였으며 웹 브라우저 상에서 목적 파일의 로딩, 단계별 실행, 종료될 때까지 실행, 시뮬레이터 종료와 같은 조작을 할 수 있음.

시뮬레이터 화면은 상단에 동작을 조작할 수 있는 상단바와 역 어셈블링 된 목적어 코드, flag 값, 레지스터 값, 현재 동작, 메모리 데이터를 볼 수 있게 구성되어 있음.
모든 데이터는 10진수가 아닌 16진수이고 레지스터 값에 한하여 10진수로 데이터를 볼 수 있음.

## 명령어 셋
### 전체 명령어 셋
|번호(hex)|명령어|길이|설명|
|:-:|:--|:-:|:---|
|00|halt|1B|CPU 동작 정지|
|10|nop|1B|No operation|
|20|rrmovq rA,rB|2B|register -> register|
|21|cmovle rA,rB|2B|비교 값이 작거나 같을 때 레지스터의 값을 레지스터로 복사|
|22|cmovl rA,rB|2B|비교 값이 작을 때 레지스터의 값을 복사|
|23|cmove rA,rB|2B|비교 값이 같을 때 레지스터의 값을 복사|
|24|cmovne rA,rB|2B|비교 값이 같지 않을 때 레지스터의 값을 복사|
|26|cmovg rA,rB|2B|비교 값이 클 때 레지스터의 값을 복사|
|30|irmovq const,rB|10B|레지스터를 정수로 초기화|
|40|rmmovq rA,D(rB)|10B|레지스터의 값을 메모리로 복사|
|50|mrmovq D(rB),rA|10B|메모리의 값을 레지스터로 복사|
|60|addq rA,rB|2B|rB = rB + rA|
|61|subq rA,rB|2B|rB = rB - rA|
|62|andq rA,rB|2B|rB = rB & rA|
|63|xorq rA,rB|2B|rB = rB ^ rA|
|64|or rA,rB|2B|rB = rB | rA|
|65|shl rA,rB|2B|rB = rB << rA|
|66|shr rA,rB|2B|rB = rB >> rA (logical)|
|67|sar rA,rB|2B|rA = rB >> rA (arithmetics)|
|68|cmp rA,rB|2B|null =  rB - rA|
|69|test rA,rB|2B|null = rB & rA|
|70|jmp const|9B|const로 점프|
|71|jle const|9B|비교 값이 작거나 같을 때 점프|
|72|jl const|9B|비교 값이 작을 때 점프|
|73|je const|9B|비교 값이 같을 때 점프|
|74|jne const|9B|비교 값이 같지 않을 때 점프|
|75|jge const|9B|비교 값이 같거나 클 때 점프|
|80|call const|9B|const 위치의 함수 호출|
|90|ret|1B|함수를 반환|
|A0|pushq rA|2B|rA의 값을 스택에 저장|
|B0|popq rA|2B|스택의 값을 rA에 저장|
|01|.elemrkq const|8B|프로그램에 포함된 인접하고 연속된 8바이트 정수 원소의 개수. 데이터 영역은 7바이트|
|02|.dummy n|nB|더미 공간을 만들기 위한 매크로. 2 이상의 숫자만 사용 가능|
|03|.align 8|n <= 8B|8바이트 정렬을 위한 매크로. 값으로 8만 사용 가능|
|-|.quad const|8B|64비트 정수를 프로그램 자체에 기록하는 키워드|

### 추가된 명령어 셋
<pre>
번호(hex)	명령어			길이	설명
-------------------------------------------------------------------
64	shl rA,rB		2B	rB = rA << rB
65	shr rA,rB		2B	rB = rA >> rB
66	cmp rA,rB		2B	null =  rA - rB
67	test rA,rB		2B	null = rA & rB
</pre>

### 미구현 명령어 셋
<pre>
번호(hex)	명령어			길이	설명
-------------------------------------------------------------------
-		.pos(n)			nB	n의 위치로 이동하는 매크로. 해당 매크로로 특정 위치로 이동할 시
                                                이동할 위치를 정확히 파악하지 않을 경우 이미 어셈블링 된 내용을
                                                덮어쓸 수 있어 해당 기능을 삭제하였음.
                                                프로그램의 특정 위치에 빈 공간을 생성할 경우 .align 8과 .dummy
                                                또는 .quad를 사용하는 것을 권장함.
</pre>

### 어셈블리 / 역 어셈블리 전용 명령어 셋
실제 동작 시에는 역할이 없으나 역 어셈블리 시 사용되는 명령어.
<pre>
번호(hex)	명령어			길이	설명
-------------------------------------------------------------------
01	.elemrkq const		8B	프로그램에 포함된 인접하고 연속된 8바이트 정수 원소의 개수. 데이터 영역은 7바이트
02	.dummy n		nB	더미 공간을 만들기 위한 매크로. 2 이상의 숫자만 사용 가능
03	.align 8		n <= 8B	8바이트 정렬을 위한 매크로. 값으로 8만 사용 가능
</pre>

.dummy 매크로로 생성한 영역에서 처음과 끝 8바이트 영역을 초기화하지 않고 바로 읽을 시 0이 아닌 값이 인출 될 수 있음.
만일 초기화 하지 않고 바로 접근할 수 있는 경우 .dummy가 아닌 .quad 0을 연속으로 작성하는 것으로 생성하는 것을 권장함.

.elemrkq .quad 키워드로 생성한 연속된 정수 원소의 개수를 프로그램 내부에 기록하는 키워드.
따로 작성하지 않더라도 프로그램 동작에는 큰 문제는 없으나 역 어셈블링이 불가능함.
작성은 .quad로 작성 된 연속 된 정수 원소의 첫 번째 위치에 그 개수를 기록하면 된다. 단, 레이블을 통해 접근할 경우 .elemrkq와 첫 번째 .quad 사이에 레이블이 있어야 함.

예시)<br>
올바른 예시
<pre>
    .elemrkq 2
    .quad 0x1
    .quad 0x2
</pre>
<pre>
    .elemrkq 2
variables:
    .quad 0x1
    .quad 0x2
</pre>

올바르지 않은 예시
<pre>
    .elemrkq 4
    .quad 0x1
    .quad 0x2
.main:
    # 각종 프로그램 처리
    .align 8
    .quad 0x3
    .quad 0x4
</pre>
<pre>
 variables:
    .elemrkq 2
    .quad 0x1
    .quad 0x2
</pre>

## 차후 계획
### 아키텍처 및 시뮬레이터
현재 구현 된 순차동작 모델 이외에 파이프라인 모델에 대한 설계 및 제작.

파이프라인 모델에서 분기 예측 없이 조건 처리가 사용될 경우 파이프라인을 일시 중단 시키는 stall 처리를 시작으로 정적 분기 예측 기법인 BTFNT까지 고려함.

### 어셈블러 및 역 어셈블러
역 어셈블링의 동작 고도화.

현재 .dummy 및 .align으로 생성된 공백 영역의 역 어셈블링을 위해 각각 02, 03과 같은 특수한 값을 사용하고 있음.
해당 매크로로 생성된 빈 공간은 00이 여러 개 나열되나, 현재 수준의 역 어셈블러의 경우 00에 대응하는 halt를 연달아서 출력하는 형태로 밖에 동작하지 않음.
00이 연달아 생성된다는 특성을 이용하여 역 어셈블러의 동작을 고도화 하여 특수한 값으로 마킹하지 않더라도 .align이나 .dummy로 자동적으로 변환되도록 함.

단, .align 8로 생성된 공간이나 메모리 주소의 값을 8로 나누어 나머지가 1인 경우에 대해서는 .align이나 .dummy가 아닌 halt로 변환하도록 함.