/*
 * Although I call this profileUtils, currently it just has source for PINROI
 * cause that's all it needed.
 */
#include "pinRoi.h"
#include <stdlib.h>
#include <cstring>
const char* __attribute__((noinline)) __begin_pin_roi(const char *s, int *beg, int *end)
{
    char *hyphen;
    const char *colon = strrchr(s, ':');
    if (colon == NULL) {
        *beg = 0; *end = 0x7fffffff;
        return s + strlen(s);
    }
    return NULL;
}


const char* __attribute__((noinline)) __end_pin_roi(const char *s, int *beg, int *end)
{
    char *hyphen;
    const char *colon = strrchr(s, ':');
    if (colon == NULL) {
        *beg = 0; *end = 0x7fffffff;
        return s + strlen(s);
    }
    return NULL;
}
