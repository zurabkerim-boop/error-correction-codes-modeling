import random

def parity(code: str, verbose: bool = True) -> str:
    """Add parity bit to the code."""
    if code.count('1') % 2 == 0:
        code += '0'
    else:
        code += '1'
    if verbose:
        print(f'Code with parity bit: {code}')
    return code


def parity_recov(code: str, verbose: bool = True) -> tuple[str, bool]:
    """Check parity and detect errors."""
    error_detected = code.count('1') % 2 != 0
    if verbose:
        if error_detected:
            print('Corrupted data detected!')
        else:
            print('Corrupted data not detected.')
    return code, error_detected


def parity_full(code: str, verbose: bool = True) -> tuple[int, int]:
    """Run full parity bit cycle."""
    if verbose:
        print(f'\nMethod: Parity bit.\nStart packet: {code}')
    
    encoded = parity(code, verbose=verbose)
    corrupted = corruption(encoded, verbose=verbose)
    checked, error_detected = parity_recov(corrupted, verbose=verbose)
    
    is_corrected = 1 if checked[:-1] == code else 0
    is_detected = 1 if error_detected else 0
    return is_corrected, is_detected


def triple_encode(code: str, verbose: bool = True) -> str:
    """Encode using triple redundancy."""
    encoded = ''.join(3 * i for i in code)
    if verbose:
        print(f'Triplicated code: {encoded}')
    return encoded


def triple_decode(code: str, verbose: bool = True) -> tuple[str, bool]:
    """Decode and correct errors using majority vote."""
    code_list = list(code)
    error_detected = False
    
    for i in range(1, len(code), 3):
        chunk = code[i-1:i+2]
        if chunk.count('1') >= 2:
            if chunk != '111':
                error_detected = True
            code_list[i-1:i+2] = ['1', '1', '1']
        else:
            if chunk != '000':
                error_detected = True
            code_list[i-1:i+2] = ['0', '0', '0']
            
    fixed_code = ''.join(code_list)
    decoded = ''.join(fixed_code[i] for i in range(0, len(fixed_code), 3))
    
    if verbose:
        print(f'Recovered data: {fixed_code}')
        print(f'Decoded data: {decoded}')
    return decoded, error_detected


def triple_full(code: str, verbose: bool = True) -> tuple[int, int]:
    """Run full triplication cycle."""
    if verbose:
        print(f'\nMethod: Triple redundancy.\nStart packet: {code}')
        
    encoded = triple_encode(code, verbose=verbose)
    corrupted = corruption(encoded, verbose=verbose)
    decoded, error_detected = triple_decode(corrupted, verbose=verbose)
    
    is_corrected = 1 if decoded == code else 0
    is_detected = 1 if error_detected else 0
    return is_corrected, is_detected


def hamming(code: str, verbose: bool = True) -> str:
    """Encode data using Hamming (7,4)."""
    d1, d2, d3, d4 = (int(x) for x in code)
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p4 = d2 ^ d3 ^ d4
    encoded = [p1, p2, d1, p4, d2, d3, d4]
    encoded_str = ''.join(str(x) for x in encoded)
    if verbose:
        print('Hamming code:', encoded_str)
    return encoded_str


def syndrome(code: str, verbose: bool = True) -> int:
    """Calculate the error syndrome using parity checks."""
    b = [int(x) for x in code]
    s1 = b[0] ^ b[2] ^ b[4] ^ b[6]
    s2 = b[1] ^ b[2] ^ b[5] ^ b[6]
    s4 = b[3] ^ b[4] ^ b[5] ^ b[6]
    pos = s1 * 1 + s2 * 2 + s4 * 4
    if verbose:
        print('Detected error position:', pos)
    return pos


def hamming_recover(code: str, verbose: bool = True) -> tuple[str, bool]:
    """Locate and correct error using the syndrome."""
    b = [int(x) for x in code]
    pos = syndrome(code, verbose=verbose)
    error_detected = pos != 0
    
    if error_detected:
        b[pos-1] ^= 1
        
    c = ''.join(str(x) for x in b)
    result = str(b[2]) + str(b[4]) + str(b[5]) + str(b[6])
    
    if verbose:
        print('Recovered 7-bit code:', c)
        print('Decoded data:', result)
    return result, error_detected


def hamming_full(code: str, verbose: bool = True) -> tuple[int, int]:
    """Run full Hamming cycle."""
    if verbose:
        print(f'\nMethod: Hamming code.\nStart packet: {code}')
        
    encoded = hamming(code, verbose=verbose)
    corrupted = corruption(encoded, verbose=verbose)
    decoded, error_detected = hamming_recover(corrupted, verbose=verbose)
    
    is_corrected = 1 if decoded == code else 0
    is_detected = 1 if error_detected else 0
    return is_corrected, is_detected


def corruption(code: str, num_errors: int = 1, verbose: bool = True) -> str:
    """Simulate transmission errors by flipping random bits."""
    code_l = list(code)
    length = len(code)
    num_errors = min(num_errors, length)
    error_indices = random.sample(range(length), num_errors)
    for idx in error_indices:
        code_l[idx] = '1' if code_l[idx] == '0' else '0'
    corrupted = ''.join(code_l)
    if verbose:
        print(f'Damaged code (errors imitated: {num_errors}): {corrupted}')
    return corrupted


def generator() -> str:
    """Generate a random 4-bit data packet."""
    return ''.join(random.choices(['0', '1'], k=4))


if __name__ == '__main__':
    print("=" * 60)
    print("Error correction simulation")
    print("=" * 60)

    print("\n>>>Single test: ")
    single_code = generator()
    parity_full(single_code, verbose=True)
    triple_full(single_code, verbose=True)
    hamming_full(single_code, verbose=True)

    # batch test
    print("\n" + "=" * 60)
    print("Batch test: 10,000 iterations")
    print("=" * 60)

    iterations = 10000

    # Statistic counters
    total_corrected_parity, total_detected_parity = 0, 0
    total_corrected_tri, total_detected_tri = 0, 0
    total_corrected_ham, total_detected_ham = 0, 0

    for _ in range(iterations):
        sim_code = generator()
        
        # Parity bit simulation
        corr_parity, det_parity = parity_full(sim_code, verbose=False)
        total_corrected_parity += corr_parity
        total_detected_parity += det_parity
        
        # Triplication simulation
        corr_tri, det_tri = triple_full(sim_code, verbose=False)
        total_corrected_tri += corr_tri
        total_detected_tri += det_tri
        
        # Hamming simulation
        corr_ham, det_ham = hamming_full(sim_code, verbose=False)
        total_corrected_ham += corr_ham
        total_detected_ham += det_ham

    print(f'\nSimulated transmission cycles: {iterations}')
    print('\nResults:')

    pct_parity = (total_corrected_parity / total_detected_parity * 100) if total_detected_parity else 0
    pct_tri = (total_corrected_tri / total_detected_tri * 100) if total_detected_tri else 0
    pct_ham = (total_corrected_ham / total_detected_ham * 100) if total_detected_ham else 0

    print(' 1. Parity bit:')
    print(f'    - Successful recovery rate: {pct_parity:.2f}%')
    print('    - Technical note: the method detects an error but cannot locate it.')
    print('      Recovery is only possible when the parity bit itself is corrupted '
      '(1 out of 5 cases = 20.00%).')

    print('\n2. Triple redundancy:')
    print(f'    - Successful recovery rate: {pct_tri:.2f}%')
    print('    - Technical note: the method can correct a single-bit error '
      'in each 3-bit group.')
    
    print('\n3. Hamming (7,4):')
    print(f'    - Successful recovery rate: {pct_ham:.2f}%')
    print('    - Technical note: the method can locate and correct a '
      'single-bit error.')
    
    print('\nConclusion:')
    print('Triple redundancy and Hamming (7,4) can recover the original data '
      'when a single-bit error occurs.')
