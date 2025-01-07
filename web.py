import pandas as pd
import streamlit as st
from cnf import convert_to_cnf, remove_epsilon_productions, remove_unit_productions
from cyk import cyk_algorithm, format_cell_content
from cfg_grammar import RULES_CFG
import graphviz

def create_parse_tree(words, parse_table, grammar):
    """Create parse tree visualization with complete derivation steps."""
    dot = graphviz.Digraph(comment='Parse Tree')
    dot.attr(rankdir='TB')
    node_count = 0

    def add_node(symbol, pos_info=""):
        nonlocal node_count
        node_id = f"node_{node_count}"
        label = f"{symbol} {pos_info}" if pos_info else symbol
        dot.node(node_id, label)
        node_count += 1
        return node_id

    def get_terminal_derivation(word, pos):
        """Get complete derivation chain for a terminal."""
        derivation = []
        for head, bodies in grammar.items():
            for body in bodies:
                if isinstance(body, str) and body.lower() == word.lower():
                    derivation.append(head)
                    for parent_head, parent_bodies in grammar.items():
                        for parent_body in parent_bodies:
                            if isinstance(parent_body, list) and len(parent_body) == 1 and parent_body[0] == head:
                                derivation.append(parent_head)
        return list(reversed(derivation))

    def build_tree(symbol, i, j, parent_id=None):
        """Build tree showing all derivation steps."""
        current_id = add_node(symbol, f"({i+1},{j+1})")
        
        if parent_id:
            dot.edge(parent_id, current_id)

        if i == j:
            derivation = get_terminal_derivation(words[i], i)
            prev_id = current_id
            
            for category in derivation:
                node_id = add_node(category, f"({i+1},{j+1})")
                dot.edge(prev_id, node_id)
                prev_id = node_id
            
            word_id = add_node(words[i])
            dot.edge(prev_id, word_id)
            return

        for k in range(i, j):
            for head, bodies in grammar.items():
                if head != symbol:
                    continue
                for body in bodies:
                    if not isinstance(body, list) or len(body) != 2:
                        continue
                    B, C = body
                    if B in parse_table[i][k] and C in parse_table[k+1][j]:
                        build_tree(B, i, k, current_id)
                        build_tree(C, k+1, j, current_id)
                        return

    if 'K' in parse_table[0][len(words)-1]:
        build_tree('K', 0, len(words)-1)
    
    return dot

def main():
    # Set page config
    st.set_page_config(
        page_title="Parsing Kalimat Bahasa Bali Berpredikat Frasa Numeralia",
        page_icon="🏝️",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 1rem;
        }
        .stTitle {
            color: #1E3A8A;
            font-size: 5rem !important;
            margin-bottom: 1rem !important;
            text-align: center !important;
        }
        .css-1d391kg {
            padding: 2rem;
            border-radius: 1rem;
            background-color: #F3F4F6;
        }
        .stButton>button {
            width: 100%;
            background-color: #1E3A8A;
            color: white;
            padding: 0.75rem;
            border-radius: 0.5rem;
            border: none;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #1E40AF;
        }
        .dataframe {
            width: 100%;
            font-size: 0.9rem;
            border-collapse: collapse;
        }
        .dataframe td, .dataframe th {
            padding: 0.75rem;
            border: 1px solid #E5E7EB;
            text-align: center;
        }
        .css-1cbqeqf {
            border-radius: 0.5rem;
            border: 1px solid #E5E7EB;
        }
        /* Center the parse tree title and container */
        .parse-tree-title {
            text-align: center;
            color: #1E3A8A;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .parse-tree-container {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }
        .parse-tree-container > div {
            display: flex;
            justify-content: center;
        }
        /* Style for main title */
        .main-title {
            text-align: center;
            color: #1E3A8A;
            font-size: 2.5rem;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header section with centered title
    st.markdown("""
        <h1 class="main-title">Parsing Kalimat Bahasa Bali Berpredikat Frasa Numeralia</h1>
        <p style='font-size: 1.2rem; color: #4B5563; margin-bottom: 2rem; text-align: center;'>
        Website ini dapat digunakan untuk memvalidasi apakah suatu kalimat dengan frasa numeralia itu valid atau tidak. Frasa numeralia merupakan kelompok kata yang menunjukkan bilangan atau jumlah tertentu. Frasa ini sering digunakan untuk memberikan informasi tentang kuantitas, seperti angka, urutan, atau jumlah benda. Nah, kira-kira ada gak sih suatu kalimat yang predikatnya itu pakai frasa numeralia? Kalau masih bingung kira-kira seperti apa aturannya, bisa dilihat expander di bawah ini ya!
        </p>
    """, unsafe_allow_html=True)

    grammar_keys = ["K", "K1", "K2", "S", "NP", "P", "NumP", "Pel", "AdjP", "VP", "Ket", "PP"]
    vocab_keys = ["PropNoun", "Pronoun", "Noun", "Adj", "Num", "V", "Prep", "Adv", "Det"]

    # Grammar Rules section with improved styling
    with st.expander("📚 Lihat Aturan Tata Bahasa", expanded=False):
        st.markdown("""
            <h3 style='color: #1E3A8A; margin-bottom: 1rem;'>Aturan-aturan Tata Bahasa</h3>
        """, unsafe_allow_html=True)
        for lhs in grammar_keys:
            rhs_list = RULES_CFG.get(lhs, [])
            st.markdown(f"""
                <div style='background-color: white; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
                    <code>{lhs} → {' | '.join([' '.join(rhs) for rhs in rhs_list])}</code>
                </div>
            """, unsafe_allow_html=True)
      
    with st.expander("📚 Lihat Vocabulary Bahasa Bali", expanded=False):
        st.markdown("""
            <h3 style='color: #1E3A8A; margin-bottom: 1rem;'>Aturan-aturan Tata Bahasa</h3>
        """, unsafe_allow_html=True)
        for lhs in vocab_keys:
            rhs_list = RULES_CFG.get(lhs, [])
            st.markdown(f"""
                <div style='background-color: white; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
                    <code>{lhs} : {', '.join([' '.join(rhs) for rhs in rhs_list])}</code>
                </div>
            """, unsafe_allow_html=True)
                  
    # Input section with card-like styling
    st.markdown("""
        <h2 style='color: #1E3A8A; margin-top: 2rem; margin-bottom: 1rem;'>Input Kalimat</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background-color: #FEF3C7; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            ⚠️ Pastikan kalimat yang dimasukkan:
            <ul>
                <li>Tidak mengandung typo</li>
                <li>Menggunakan huruf kecil</li>
                <li>Tidak menggunakan tanda baca (kecuali tanda hubung)</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    sentence = st.text_input("", placeholder="Masukkan kalimat dalam Bahasa Bali...")
   
    if st.button("Periksa Kalimat"):
        if sentence:
            words = sentence.strip().split()
            
            with st.spinner("🔍 Memproses kalimat..."):
                cnf = convert_to_cnf(remove_unit_productions(remove_epsilon_productions(RULES_CFG)))
                is_valid, parse_table = cyk_algorithm(cnf, words)
                
                # Display parse table with improved styling
                st.markdown("""
                    <h2 style='color: #1E3A8A; margin-top: 2rem; margin-bottom: 1rem; text-align: center;'>Tabel Filling</h2>
                """, unsafe_allow_html=True)
                
                display_table = []
                n = len(words)
                for i in range(n + 1):
                    display_table.append([""] * n)
                display_table[n] = words.copy()
                for i in range(n):
                    for j in range(n - i):
                        display_table[n-1-i][j] = format_cell_content(parse_table[j][j + i])

                df = pd.DataFrame(display_table)
                st.write(df.to_html(index=False, header=False, classes='dataframe'), unsafe_allow_html=True)

                if is_valid:
                    st.markdown(f"""
                        <div style='background-color: #DEF7EC; color: #03543F; padding: 1rem; border-radius: 0.5rem; margin: 2rem 0; text-align: center;'>
                            ✅ Kalimat <strong>"{sentence}."</strong> VALID menurut tata bahasa Bali
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                        <h2 class='parse-tree-title'>Pohon Parsing</h2>
                    """, unsafe_allow_html=True)
                    
                    # Wrap the graphviz chart in a centered container
                    st.markdown("<div class='parse-tree-container'>", unsafe_allow_html=True)
                    dot = create_parse_tree(words, parse_table, cnf)
                    st.graphviz_chart(dot)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='background-color: #FDE2E2; color: #9B1C1C; padding: 1rem; border-radius: 0.5rem; margin: 2rem 0; text-align: center;'>
                            ❌ Kalimat <strong>"{sentence}."</strong> TIDAK VALID menurut tata bahasa Bali
                        </div>
                    """, unsafe_allow_html=True)
                    
if __name__ == "__main__":
    main()