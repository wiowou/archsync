cppsourceTest='''#define MYDEBUG

#include "../src/${name}.h"

${namespaces}
class ${Name}Test
{
public:

  int Exec()
  {
    ${Name} ${name};
    int i = 0;
    
    return i;
  }

};

${Enamespaces}

int main()
{
  ${namespacePrefix}${Name}Test test;
  return test.Exec();
}'''