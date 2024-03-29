# Y86-64+ 시뮬레이터
## 개요
대학교 학부 과정 중 컴퓨터 구조 수업 시간에 사용되는 Y86-64( http://csapp.cs.cmu.edu/ )의 개선버전.
오리지널 버전의 Y86-64에 일부 명령어를 새롭게 추가한 후 파이썬으로 재구성하여 제작됨.

## 의존성 패키지
- flask

## 사용 방법
### 시뮬레이션
1. 파이썬을 이용하여 simulator.py를 실행한 후 웹 브라우저로 접속(기본 값 기준 localhost:5500으로 접속)
2. 초기 화면에서 NEW 탭을 선택할 경우 새로운 세션을 생성할 수 있음. RESTART 탭을 선택할 경우 UUID 입력으로 이전에 실행한 세션을 다시 시작할 수 있음
3. 텍스트 필드에 목적 파일의 경로를 입력한 후 LOAD를 클릭해 목적 파일을 적재
4. RESTART, STEP, RUN을 이용하여 프로그램을 다시 시작하거나 한 단계씩 또는 끝까지 실행할 수 있음
5. SHUTDOWN으로 현재 세션을 종료 할 수 있음

### 프로그램 작성
1. 시뮬레이터 실행 후 Object Code 영역을 클릭
2. List of Examples에서 예제 파일을 선택하거나 우측 텍스트 영역에 어셈블리 코드 작성
3. 우측 하단의 ASSEMBLE 버튼을 클릭하여 어셈블 진행
4. 어셈블이 정상적으로 완료되면 시뮬레이터 화면으로 넘어가고, 오류가 있을 경우 alert이 나오며 오류 코드를 표시함

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
|6A|not rA,rB|2B|rB = ~rA|
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
|번호(hex)|명령어|길이|설명|
|:-:|:--|:-:|:---|
|64|or rA,rB|2B|rB = rB | rA|
|65|shl rA,rB|2B|rB = rB << rA|
|66|shr rA,rB|2B|rB = rB >> rA (logical)|
|67|sar rA,rB|2B|rA = rB >> rA (arithmetics)|
|68|cmp rA,rB|2B|null =  rB - rA|
|69|test rA,rB|2B|null = rB & rA|
|6A|not rA,rB|2B|rB = ~rA|

### 어셈블리 / 역 어셈블리 전용 명령어 셋
실제 동작 시에는 역할이 없으나 역 어셈블리 시 사용되는 명령어.
<pre>
번호(hex)	명령어			길이	설명
-------------------------------------------------------------------
01	.elemrkq const		8B	프로그램에 포함된 인접하고 연속된 8바이트 정수 원소의 개수. 데이터 영역은 7바이트
02	.dummy n		nB	더미 공간을 만들기 위한 매크로. 2 이상의 숫자만 사용 가능
03	.align 8		n <= 8B	8바이트 정렬을 위한 매크로. 값으로 8만 사용 가능
</pre>

.dummy 지시어로 생성한 영역에서 처음과 끝 8바이트 영역을 초기화하지 않고 바로 읽을 시 0이 아닌 값이 인출 될 수 있음.
만일 초기화 하지 않고 바로 접근할 수 있는 경우 .dummy가 아닌 .quad 0을 연속으로 작성하는 것으로 생성하는 것을 권장함.

.elemrkq 지시어는 .quad 키워드로 생성한 연속된 정수 원소의 개수를 프로그램 내부에 기록하는 키워드.
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

## 알려진 문제점
### 시뮬레이터
파이프라인 모델의 경우 memiotest.yps 예제를 포함한 일부 코드가 정상적으로 동작하지 않는 문제점이 존재함

### 어셈블러
다음과 같은 문법은 어셈블이 되지 않고 오류 메시지를 표출함
<pre>
    mrmovq label,%rdx # -> mrmovq label(%null),%rdx로 수정하여 작성할 것
    rmmovq %rdx,label # -> mrmovq %rdx,label(%null)로 수정하여 작성할 것
</pre>
