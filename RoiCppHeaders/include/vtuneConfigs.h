#ifndef VTUNE_CONFIGS_H
#define VTUNE_CONFIGS_H

#if (VTUNE_ENABLED==1)
  #include <ittnotify.h>
  #define BEGIN_VTUNE_ROI __itt_resume();
  #define END_VTUNE_ROI __itt_pause();
#else
  #define BEGIN_VTUNE_ROI
  #define END_VTUNE_ROI
#endif //VTUNE_ENABLED

  
#endif //VTUNE_CONFIGS_H
