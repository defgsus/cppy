#include <vector>

#include "py_utils.h"
#include "example.h"

int main(int argc, char** argv)
{
    // convert char** to wchar**
    std::vector<std::wstring> swargs;
    wchar_t* wargs[argc];
    for (int i=0; i<argc; ++i)
    {
        std::wstring str;
        str.resize(4096);
        swprintf(&str[0], 4095, L"%hs", argv[i]);
        swargs.push_back(str);
        wargs[i] = &swargs.back()[0];
    }

    // append module to inittab
    initialize_module_example();

    // run python
    Py_Main(argc, wargs);

    return 0;
}
