#include<iostream>
#include<fstream>

using namespace std;

int main () {
  ofstream myfile;
  myfile.open ("example.txt");
  myfile << "Writing this to a file.\n";
  char a,b;
  a='A';
  b='A';
  for(int i =0;i<2;++i)
  {
  	for(int j=0;j<26;++j)
  	{
  	char n=b+j;
  	char m=a+i;
  	myfile<<m;
  	myfile<<n;
  	myfile<<endl;
  	}
  }
  myfile.close();
  return 0;
}