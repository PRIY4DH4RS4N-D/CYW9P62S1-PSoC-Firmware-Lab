#include "gesture.h"
#include <stdio.h>
static void emit(const char *t,int v,char m,void *u) {
    (void)u; printf("%s %d %c\n",t,v,m);
}
int main(void) {
    cap_gesture g={0}; unsigned ms; int b1,b2,pos;
    while(scanf("%u %d %d %d",&ms,&b1,&b2,&pos)==4)
        cap_step(&g,ms,b1!=0,b2!=0,pos,emit,0);
    return 0;
}
