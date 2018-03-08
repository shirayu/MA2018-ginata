#include <iostream>
#include <cstring>
#include <mecab.h>
#include <vector>
#include <string>
#include <sstream>

#define CHECK(eval)                                                            \
    if (!eval) {                                                               \
        const char *e = tagger ? tagger->what() : MeCab::getTaggerError();     \
        std::cerr << "Exception:" << e << std::endl;                           \
        delete tagger;                                                         \
        return false;                                                          \
    }

bool myparse(const MeCab::Tagger *tagger, MeCab::Lattice *lattice,
             const char *text, const std::vector<std::string> &words,
             size_t inside_position) {
    //未知語があれば解析失敗とする
    lattice->set_sentence(text);
    if (inside_position == 0) { //特別扱い
        size_t posit = 0;
        for (const auto &word : words) {
            posit += word.size();
            if (posit == std::strlen(text)) { //最終形態素は除外
                continue;
            };

            lattice->set_boundary_constraint(posit, MECAB_TOKEN_BOUNDARY);
        };
    } else {
        lattice->set_boundary_constraint(inside_position, MECAB_INSIDE_TOKEN);
    }

    CHECK(tagger->parse(lattice));

    {
        bool unk = false;
        for (auto node = lattice->bos_node(); node; node = node->next) {
            if (node->stat == MECAB_UNK_NODE) {
                unk = true;
            }
        }
        if (unk) {
            return false;
        };
    }
    CHECK(lattice->bos_node());
    return true;
}

void myprint(MeCab::Lattice *lattice) {
    std::stringstream fs_pos;
    std::stringstream fs_lid;

    for (auto node = lattice->bos_node(); node; node = node->next) {
        if (node->stat == MECAB_BOS_NODE) {
            continue;
        } else if (node->stat == MECAB_EOS_NODE) {
            continue;
        }

        std::cout << "|";
        std::cout.write(node->surface, node->length);
        const auto f = std::string(node->feature);
        const auto posit_com = f.find(",");
        if (posit_com != std::string::npos) {
            fs_pos << "|" << f.substr(0, posit_com);
        }

        const auto posit_lid_end = f.rfind(",");
        if (posit_lid_end != std::string::npos) {
            const auto posit_lid_beg = f.rfind(",", posit_lid_end - 1 - 1);
            if (posit_lid_beg != std::string::npos) {
                fs_lid << "|"
                       << f.substr(posit_lid_beg + 1,
                                   posit_lid_end - posit_lid_beg - 1);
            }
        }
    }
    std::cout << "|";
    std::cout << "\t" << lattice->eos_node()->cost;
    std::cout << "\t" << fs_pos.str() << "|";
    std::cout << "\t" << fs_lid.str() << "|";
}

void get_ginata(const MeCab::Tagger *tagger, MeCab::Lattice *lattice_orig,
                MeCab::Lattice *lattice_ginata, const std::string &line) {
    const auto posit_tab = line.find("\t");
    if (posit_tab == std::string::npos) {
        return;
    }
    const auto freq_str = line.substr(posit_tab + 1);
    std::vector<std::string> words;
    std::string text_str;
    {
        std::stringstream ss(line.substr(0, posit_tab));
        std::string buffer;
        while (std::getline(ss, buffer, ' ')) {
            words.push_back(buffer);
            text_str += buffer;
        }
    }

    if (!myparse(tagger, lattice_orig, text_str.c_str(), words, 0)) {
        return;
    }
    size_t posit = 0;
    // TODO 重複するginataの出力を省略する(3-gram以上の入力で重複の可能性有)
    for (const auto &word : words) {
        if (posit == 0) {
            posit += word.size();
            continue;
        }

        if (!myparse(tagger, lattice_ginata, text_str.c_str(), words, posit)) {
            continue;
        }
        std::cout << freq_str << "\t";
        myprint(lattice_orig);
        std::cout << "\t";
        myprint(lattice_ginata);
        std::cout << std::endl;
        posit += word.size();
    }
}

int main(int argc, char **argv) {
    auto model = MeCab::createModel(argc, argv);
    auto tagger = model->createTagger();
    CHECK(tagger)

    auto lattice_orig = model->createLattice();
    auto lattice_ginata = model->createLattice();

    std::string line;
    while (std::getline(std::cin, line)) {
        get_ginata(tagger, lattice_orig, lattice_ginata, line);
    }

    delete lattice_orig;
    delete lattice_ginata;
    delete tagger;
    delete model;

    return 0;
}
