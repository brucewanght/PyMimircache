//
//  reader.h
//  LRUAnalyzer
//
//  Created by Juncheng on 5/25/16.
//  Copyright © 2016 Juncheng. All rights reserved.
//

#ifndef reader_h
#define reader_h

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <unistd.h>
#include <glib.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>


#include "const.h"
#include "libcsv.h"


#define LINE_ENDING '\n'
#define BINARY_FMT_MAX_LEN 32


// trace type
#define CSV 'c'
#define PLAIN 'p'
#define VSCSI 'v'
#define BINARY 'b'



// data type
#define DT_NUMBER 'l'
#define DT_STRING 'c'



typedef struct break_point{
    GArray* array;
    char mode;                  // r or v
    guint64 time_interval;
}break_point_t;


typedef struct{
    gpointer item_p;
    char item[cache_line_label_size];
    char type;                              /* type of content can be either guint64(l) or char*(c) */
    guint64 ts;                             /* deprecated, should not use, virtual timestamp */
    size_t size;
    int op;
    guint64 real_time;
    gboolean valid;
    
    unsigned char traceID;                           /* this is for mixed trace */
    void *content;                                   /* the content of page/request */
    guint size_of_content;                           /* the size of mem area content points to */
    
    
}cache_line;


// declare reader struct 
struct reader;

typedef struct reader_base{
    
    char type;                              /* possible types: c(csv), v(vscsi),
                                             * p(plain text), b(binaryReader)  */
    char data_type;                         /* possible types: l(guint64), c(char*) */
    
    FILE* file;
    char file_loc[FILE_LOC_STR_SIZE];
    size_t file_size; 
    void* init_params;
    
    void* mapped_file;                      /* mmap the file, this should not change during runtime
                                             * offset in the file is changed using offset */
    guint64 offset;
    size_t record_size;                     /* the size of one record, used to
                                             * locate the memory location of next element,
                                             * used in vscsiReaser and binaryReader */
    
    gint64 total_num;                       /* number of records */
    
    
    gint ver;
    
    void* params;                           /* currently not used */
    

} reader_base_t;


typedef struct reader_data_unique{

    double* hit_rate;
    double log_base;

}reader_data_unique_t;


typedef struct reader_data_share{
    break_point_t *break_points;
    gint64* reuse_dist;
    char reuse_dist_type;                  // NORMAL_REUSE_DISTANCE or FUTURE_REUSE_DISTANCE 
    gint64 max_reuse_dist;
    gint* last_access;
    
}reader_data_share_t;



//typedef struct reader_base reader_base_t;
typedef struct reader{
    struct reader_base* base;
    struct reader_data_unique* udata;
    struct reader_data_share* sdata; 
    void* reader_params;
}reader_t;









reader_t* setup_reader(const char* file_loc,
                       const char file_type,
                       const char data_type,
                       const void* const setup_params);

void read_one_element(reader_t *const reader,
                      cache_line *const c);

guint64 skip_N_elements(reader_t *const reader,
                        const guint64 N);

int go_back_one_line(reader_t *const reader);

int go_back_two_lines(reader_t *const reader);

void read_one_element_above(reader_t *const reader,
                            cache_line *const c);

int read_one_request_all_info(reader_t *const reader,
                              void* storage);

guint64 read_one_timestamp(reader_t *const reader);

void read_one_op(reader_t *const reader, void* op);

guint64 read_one_request_size(reader_t *const reader);


void reader_set_read_pos(reader_t *const reader, double pos);

guint64 get_num_of_cache_lines(reader_t *const reader);

void reset_reader(reader_t *const reader);

int close_reader(reader_t *const reader);

int close_reader_unique(reader_t *const reader);

reader_t* clone_reader(reader_t *const reader);

void set_no_eof(reader_t *const reader);


cache_line* new_cacheline(void);

void destroy_cacheline(cache_line* cp);



#endif /* reader_h */
