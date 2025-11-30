#include "postfix_eval.h"
#include "stack.h"
#include "tokens.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NOTANUMBER 100001
#define MAX 100000
#define MIN -100000

#define FREE_ALL                                                               \
  {                                                                            \
    stack_clear(&token_stack);                                                 \
    free(tokens_copy);                                                         \
    tokens_copy = NULL;                                                        \
    return 1;                                                                  \
  }

typedef enum {
  F_UNDEFINED,
  SIN,
  COS,
  TAN,
  SINH,
  COSH,
  TANH,
  ASIN,
  ACOS,
  ATAN,
  ABS,
  LOG,
  LN,
  EXP
} functions;

typedef enum { O_UNDEFINED, ADD, SUB, MUL, DIV, POW } operators;

int get_operator(Token *operator) {
  if (operator == NULL)
    return 0;

  if (!strcmp(operator->value, "+"))
    return ADD;
  if (!strcmp(operator->value, "-"))
    return SUB;
  if (!strcmp(operator->value, "*"))
    return MUL;
  if (!strcmp(operator->value, "/"))
    return DIV;
  if (!strcmp(operator->value, "^"))
    return POW;

  return O_UNDEFINED;
}

int eval_operator(Token *fr_number, Token *sec_number, Token *oper,
                  Token *result) {
  int otype = 0;
  double num1 = 0;
  double num2 = 0;
  double r = 0;
  char *endptr = NULL;

  /* sanity check */
  if (fr_number == NULL)
    return 0;
  if (sec_number == NULL)
    return 0;
  if (oper == NULL)
    return 0;
  if (result == NULL)
    return 0;

  num1 = strtod(fr_number->value, &endptr);
  if (*endptr != '\0')
    return 0;

  num2 = strtod(sec_number->value, &endptr);
  if (*endptr != '\0')
    return 0;

  otype = get_operator(oper);

  switch (otype) {
  case ADD:
    r = num1 + num2;
    break;

  case SUB:
    r = num1 - num2;
    break;

  case MUL:
    r = num1 * num2;
    break;

  case DIV:
    if (num2 == 0) {
      r = NOTANUMBER;
    } else
      r = num1 / num2;
    break;

  case POW:
    r = pow(num1, num2);
    break;

  default:
    return O_UNDEFINED;
    break;
  }

  if (r == NOTANUMBER) {
    result->type = TOKEN_NUMBER;
    sprintf(result->value, "%d", NOTANUMBER);
    return 1;
  }

  r = r > MAX ? MAX : (r < MIN ? MIN : r);

  result->type = TOKEN_NUMBER;
  sprintf(result->value, "%f", r);

  return 1;
}

int get_function(Token *func) {
  /* sanity check */
  if (func == NULL)
    return 0;

  if (!strcmp(func->value, "sin"))
    return SIN;
  if (!strcmp(func->value, "cos"))
    return COS;
  if (!strcmp(func->value, "tan"))
    return TAN;
  if (!strcmp(func->value, "sinh"))
    return SINH;
  if (!strcmp(func->value, "cosh"))
    return COSH;
  if (!strcmp(func->value, "tanh"))
    return TANH;
  if (!strcmp(func->value, "asin"))
    return ASIN;
  if (!strcmp(func->value, "acos"))
    return ACOS;
  if (!strcmp(func->value, "atan"))
    return ATAN;
  if (!strcmp(func->value, "abs"))
    return ABS;
  if (!strcmp(func->value, "log"))
    return LOG;
  if (!strcmp(func->value, "ln"))
    return LN;
  if (!strcmp(func->value, "exp"))
    return EXP;

  return F_UNDEFINED;
}

int eval_function(Token *number, Token *func, Token *result) {
  int ftype = 0;
  double num = 0;
  char *endptr = NULL;
  double r = 0;

  /* sanity check */
  if (number == NULL)
    return 0;
  if (func == NULL)
    return 0;
  if (result == NULL)
    return 0;

  num = strtod(number->value, &endptr);
  if (*endptr != '\0')
    return 0;

  ftype = get_function(func);

  switch (ftype) {
  case SIN:
    r = sin(num);
    break;

  case COS:
    r = cos(num);
    break;

  case TAN:
    r = tan(num);
    break;

  case SINH:
    r = sinh(num);
    break;

  case COSH:
    r = cosh(num);
    break;

  case TANH:
    r = tanh(num);
    break;

  case ASIN:
    if (num < -1 || num > 1) {
      r = NOTANUMBER;
    } else
      r = asin(num);
    break;

  case ACOS:
    if (num < -1 || num > 1) {
      r = NOTANUMBER;
    } else
      r = acos(num);
    break;

  case ATAN:
    r = atan(num);
    break;

  case ABS:
    r = fabs(num);
    break;

  case LOG:
    if (num <= 0) {
      r = NOTANUMBER;
    } else
      r = log10(num);
    break;

  case LN:
    if (num <= 0) {
      r = NOTANUMBER;
    } else
      r = log(num);
    break;

  case EXP:
    r = exp(num);
    break;

  default:
    return F_UNDEFINED;
    break;
  }

  if (r == NOTANUMBER) {
    result->type = TOKEN_NUMBER;
    sprintf(result->value, "%d", NOTANUMBER);
    return 1;
  }

  r = r > MAX ? MAX : (r < MIN ? MIN : r);

  result->type = TOKEN_NUMBER;
  sprintf(result->value, "%f", r);

  return 1;
}

int postfix_eval(Token *token_arr, int tokens_count, double x, double *result) {
  Token *tokens_copy;
  stack *token_stack = NULL;
  Token *current = NULL;

  Token *token_on_top = NULL;
  Token *num1 = NULL;
  Token *num2 = NULL;

  char *endptr = NULL;

  double num = 0;
  int error = 0;
  int wrong_func_output = 0;
  int wrong_op_output = 0;
  int i = 0;

  /* sanity check */
  if (token_arr == NULL) {
    return 0;
  }
  if (result == NULL) {
    return 0;
  }
  if (tokens_count <= 0) {
    return 0;
  }

  *result = NOTANUMBER;

  token_stack = stack_create((unsigned int)tokens_count);
  if (token_stack == NULL) {
    return 0;
  }

  tokens_copy = (Token *)malloc(sizeof(Token) * tokens_count);
  memcpy(tokens_copy, token_arr, sizeof(Token) * tokens_count);

  for (i = 0; i < tokens_count; i++) {
    current = &(tokens_copy[i]);

    if (current->type == TOKEN_NUMBER) {
      if (stack_push(token_stack, current) == 0) {
        error = 1;
        break;
      }
      continue;
    }

    if (current->type == TOKEN_VARIABLE) {
      current->type = TOKEN_NUMBER;
      sprintf(current->value, "%f", x);

      if (stack_push(token_stack, current) == 0) {
        error = 1;
        break;
      }
      continue;
    }

    if (current->type == TOKEN_UNARY_OPERATOR) {
      token_on_top = stack_pop(token_stack);
      if (token_on_top == NULL) {
        error = 1;
        break;
      }

      num = strtod(token_on_top->value, &endptr);
      if (*endptr != '\0') {
        error = 1;
        break;
      }

      num = -num;
      sprintf(token_on_top->value, "%f", num);

      if (stack_push(token_stack, token_on_top) == 0) {
        error = 1;
        break;
      }
      continue;
    }

    if (current->type == TOKEN_FUNCTION) {
      token_on_top = stack_pop(token_stack);
      if (token_on_top == NULL) {
        error = 1;
        break;
      }

      if (eval_function(token_on_top, current, token_on_top) == 0) {
        error = 1;
        break;
      }

      if (stack_push(token_stack, token_on_top) == 0) {
        error = 1;
        break;
      }
      continue;
    }

    if (current->type == TOKEN_BINARY_OPERATOR) {
      num2 = stack_pop(token_stack);
      num1 = stack_pop(token_stack);

      if (num1 == NULL) {
        error = 1;
        break;
      }

      if (eval_operator(num1, num2, current, num1) == 0) {
        error = 1;
        break;
      }

      if (stack_push(token_stack, num1) == 0) {
        error = 1;
        break;
      }
      continue;
    }
  }

  if (error)
    FREE_ALL;

  token_on_top = stack_pop(token_stack);
  if (token_on_top == NULL)
    FREE_ALL;
  if (stack_peek(token_stack) != NULL)
    FREE_ALL;

  num = strtod(token_on_top->value, &endptr);
  if (*endptr != '\0')
    FREE_ALL;

  *result = num;
  free(tokens_copy);
  stack_clear(&token_stack);

  return 1;
}
