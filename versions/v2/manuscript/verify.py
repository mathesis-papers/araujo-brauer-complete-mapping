import itertools
import json
import math


BASE_TWO = [((1, 3), (0, 3)), ((2, 3), (2, 4)),
            ((0, 4), (0, 5)), ((3, 4), (1, 4)),
            ((3, 5), (1, 5)), ((4, 5), (2, 5))]
BASE_THREE = [((0, 1, 2), (0, 1, 4)), ((0, 3, 4), (0, 2, 4)),
              ((1, 2, 4), (1, 2, 5)), ((1, 3, 4), (1, 3, 5)),
              ((2, 3, 4), (2, 3, 5)), ((2, 4, 5), (0, 2, 5)),
              ((3, 4, 5), (0, 3, 5)), ((0, 1, 5), (0, 1, 6)),
              ((0, 4, 5), (0, 4, 6)), ((1, 4, 5), (1, 4, 6)),
              ((1, 5, 6), (0, 5, 6)), ((4, 5, 6), (2, 4, 6)),
              ((2, 5, 6), (0, 2, 6)), ((1, 2, 6), (1, 3, 6)),
              ((3, 4, 6), (0, 3, 6)), ((3, 5, 6), (2, 3, 6))]
FOUR_PAIRS = [((0,), (1,)), ((2,), (3,)),
              ((0, 1), (0, 2)), ((0, 3), (1, 3)), ((1, 2), (2, 3)),
              ((0, 1, 2), (0, 1, 3)), ((0, 2, 3), (1, 2, 3))]


def pair_dictionary(pairs):
    result = {}
    for first, second in pairs:
        first, second = frozenset(first), frozenset(second)
        assert first not in result and second not in result
        result[first], result[second] = second, first
    return result


def subset_partner(subset, degree, rank):
    base_degree = 6 if rank == 2 else 7
    if degree == base_degree:
        return pair_dictionary(BASE_TWO if rank == 2 else BASE_THREE).get(subset, subset)
    old_degree = degree - 4
    old = frozenset(vertex for vertex in subset if vertex < old_degree)
    new = frozenset(vertex - old_degree for vertex in subset if vertex >= old_degree)
    if not new:
        return subset_partner(old, old_degree, rank)
    return old | frozenset(vertex + old_degree for vertex in pair_dictionary(FOUR_PAIRS)[new])


def matchings(vertices, partial=False):
    if not vertices:
        yield ()
        return
    first, *remaining = vertices
    if partial:
        for rest in matchings(remaining, partial):
            yield ((first,),) + rest
    for position, second in enumerate(remaining):
        leftover = remaining[:position] + remaining[position + 1:]
        for rest in matchings(leftover, partial):
            yield ((first, second),) + rest


def half_diagrams(degree, rank, partial=False):
    result = []
    for through in itertools.combinations(range(degree), rank):
        complement = [vertex for vertex in range(degree) if vertex not in through]
        for pairing in matchings(complement, partial):
            result.append((through, pairing))
    return result


def compose(first, second):
    return tuple(second[first[position]] for position in range(len(first)))


def inverse(permutation):
    return tuple(permutation.index(position) for position in range(len(permutation)))


def sign(permutation):
    inversions = sum(first > second for position, first in enumerate(permutation)
                     for second in permutation[position + 1:])
    return -1 if inversions % 2 else 1


def connector(first, second):
    through_first, pairing_first = first
    through_second, pairing_second = second
    vertices = set(through_first) | set(through_second)
    for block in pairing_first + pairing_second:
        vertices.update(block)
    parent = {vertex: vertex for vertex in vertices}

    def find(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for block in pairing_first + pairing_second:
        if len(block) == 2:
            parent[find(block[0])] = find(block[1])
    transport = []
    for vertex in through_first:
        partners = [position for position, target in enumerate(through_second)
                    if find(vertex) == find(target)]
        if len(partners) != 1:
            return None
        transport.append(partners[0])
    return tuple(transport) if len(set(transport)) == len(through_first) else None


def signed_cycles(halves, degree, rank):
    lookup = {half: position for position, half in enumerate(halves)}
    fibres = {}
    for position, half in enumerate(halves):
        fibres.setdefault(frozenset(half[0]), []).append(position)
    permutation = {}
    unmatched = []
    for through, fibre in fibres.items():
        other = subset_partner(through, degree, rank)
        if through != other:
            for first, second in zip(fibre, fibres[other], strict=True):
                permutation[first] = second
        else:
            assert len(fibre) % 2 == 1
            unmatched.append(fibre[0])
            for first, second in zip(fibre[1::2], fibre[2::2], strict=True):
                permutation[first], permutation[second] = second, first
    assert len(unmatched) == 3
    for position, first in enumerate(unmatched):
        permutation[first] = unmatched[(position + 1) % 3]
    assert set(permutation) == set(lookup.values()) == set(permutation.values())
    weights = {}
    for first, second in permutation.items():
        transport = connector(halves[first], halves[second])
        assert transport is not None and first != second
        weights[first] = sign(transport)
    potential = {}
    for first in range(len(halves)):
        if first in potential:
            continue
        potential[first] = 1
        current = first
        while True:
            following = permutation[current]
            value = -weights[current] * potential[current]
            if following == first:
                assert potential[first] == value
                break
            assert following not in potential
            potential[following] = value
            current = following
    return permutation, potential


def signed_map(index_first, group_sign, index_last, count, permutation, potential):
    parameter = group_sign * potential[index_last]
    target_last = index_last if parameter == 1 else permutation[index_last]
    return (target_last, -potential[target_last] * parameter,
            (index_first + target_last) % count)


def even_map(index_first, group_sign, index_last, count):
    half_count = count // 2
    first_bit, first_residue = divmod(index_first, half_count)
    last_bit, last_residue = divmod(index_last, half_count)
    group_bit = 0 if group_sign == 1 else 1
    new_bit = (first_bit + group_bit) % 2
    new_last = new_bit * half_count + (first_residue + last_residue) % half_count
    return index_last, (-1) ** ((first_bit + last_bit) % 2), new_last


def lift_entry(sandwich, input_group, output_sign):
    rank = len(sandwich)
    identity = tuple(range(rank))
    transposition = (1, 0, 2)
    input_section = identity if sign(input_group) == 1 else transposition
    target_section = identity if sign(input_group) * sign(sandwich) * output_sign == 1 else transposition
    normal = compose(input_group, inverse(input_section))
    return compose(compose(compose(inverse(sandwich), inverse(input_section)), normal), target_section)


def coordinate_diagram(upper, group, lower, degree):
    blocks = list(upper[1])
    blocks.extend(tuple(vertex + degree for vertex in block) for block in lower[1])
    blocks.extend((vertex, degree + lower[0][group[position]])
                  for position, vertex in enumerate(upper[0]))
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def diagram_product(first, second, degree):
    parent = list(range(3 * degree))

    def find(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for shift, diagram in [(0, first), (degree, second)]:
        for block in diagram:
            for vertex in block[1:]:
                parent[find(block[0] + shift)] = find(vertex + shift)
    components = {}
    for exterior in range(2 * degree):
        internal = exterior if exterior < degree else exterior + degree
        components.setdefault(find(internal), []).append(exterior)
    return tuple(sorted(tuple(block) for block in components.values()))


def verify_factor(degree, rank, partial=False):
    halves = half_diagrams(degree, rank, partial)
    count = len(halves)
    assert count
    permutations = list(itertools.permutations(range(rank)))
    if count % 2:
        cycle, potential = signed_cycles(halves, degree, rank)
        mapping = lambda first, group, last: signed_map(first, group, last, count, cycle, potential)
    else:
        mapping = lambda first, group, last: even_map(first, group, last, count)
    multipliers, products = set(), set()
    for first in range(count):
        for last in range(count):
            for group in permutations:
                column_first, column_sign, column_last = mapping(first, sign(group), last)
                sandwich = connector(halves[last], halves[column_first])
                assert sandwich is not None
                if rank == 2:
                    column_group = (0, 1) if column_sign == 1 else (1, 0)
                else:
                    column_group = lift_entry(sandwich, group, column_sign)
                assert sign(column_group) == column_sign
                product_group = compose(compose(group, sandwich), column_group)
                first_diagram = coordinate_diagram(halves[first], group, halves[last], degree)
                second_diagram = coordinate_diagram(halves[column_first], column_group, halves[column_last], degree)
                expected_diagram = coordinate_diagram(halves[first], product_group, halves[column_last], degree)
                assert diagram_product(first_diagram, second_diagram, degree) == expected_diagram
                multipliers.add((column_first, column_group, column_last))
                products.add((first, product_group, column_last))
    expected = count * count * math.factorial(rank)
    assert len(multipliers) == len(products) == expected
    return {'degree': degree, 'rank': rank, 'partial': partial,
            'half_diagrams': count, 'elements': expected,
            'exterior_connectivity_products_checked': expected,
            'multiplier_and_product_bijections': True}


def verify_trivial_factor(degree, rank, partial):
    halves = half_diagrams(degree, rank, partial)
    count = len(halves)
    identity = tuple(range(rank))
    multipliers, products = set(), set()
    for first in range(count):
        for last in range(count):
            output_last = (first + last) % count
            multiplier = (last, identity, output_last)
            product = (first, identity, output_last)
            row_diagram = coordinate_diagram(halves[first], identity, halves[last], degree)
            column_diagram = coordinate_diagram(halves[last], identity, halves[output_last], degree)
            expected = coordinate_diagram(halves[first], identity, halves[output_last], degree)
            assert diagram_product(row_diagram, column_diagram, degree) == expected
            multipliers.add(multiplier)
            products.add(product)
    assert len(multipliers) == len(products) == count ** 2
    return {'degree': degree, 'rank': rank, 'partial': partial,
            'elements': count ** 2, 'bijections_and_direct_products': True}


def verify_small_boundaries():
    trivial_factors = []
    for degree in range(1, 4):
        for partial in [False, True]:
            for rank in range(min(1, degree) + 1):
                if half_diagrams(degree, rank, partial):
                    trivial_factors.append(verify_trivial_factor(degree, rank, partial))
    degree, rank = 3, 2
    halves = half_diagrams(degree, rank, True)
    assert len(halves) == 3
    permutations = list(itertools.permutations(range(rank)))
    triples = list(itertools.product(range(3), permutations, range(3)))
    for first in range(3):
        for second in range(3):
            assert connector(halves[first], halves[second]) == ((0, 1) if first == second else None)
    products_checked = 0
    for first, group, last in triples:
        for column_first, column_group, column_last in triples:
            row = coordinate_diagram(halves[first], group, halves[last], degree)
            column = coordinate_diagram(halves[column_first], column_group, halves[column_last], degree)
            product = diagram_product(row, column, degree)
            through = sum(any(vertex < degree for vertex in block) and
                          any(vertex >= degree for vertex in block) for block in product)
            assert (through == rank) == (last == column_first)
            if last == column_first:
                expected = coordinate_diagram(halves[first], compose(group, column_group),
                                              halves[column_last], degree)
                assert product == expected
            products_checked += 1
    negatives = sum(sign(group) == -1 for first, group, last in triples)
    assert len(triples) == 18 and negatives == 9 and products_checked == 324
    unit_obstructions = []
    for degree in [2, 3]:
        negatives_in_group = sum(sign(group) == -1 for group in itertools.permutations(range(degree)))
        assert negatives_in_group % 2 == 1
        unit_obstructions.append({'degree': degree, 'negative_sign_elements': negatives_in_group})
    return {'trivial_group_factors': trivial_factors,
            'partial_brauer_three_rank_two': {'nonzero_elements': 18, 'negative_sign_elements': 9,
                                             'diagonal_sandwich_only': True,
                                             'exterior_products_checked': products_checked},
            'unit_obstructions': unit_obstructions}


def verify_rectangular_enumeration():
    indices = list(itertools.product(range(2), repeat=2))
    brute_force = set()
    for images in itertools.permutations(indices):
        products = {(row[0], column[1]) for row, column in zip(indices, images, strict=True)}
        if len(products) == 4:
            brute_force.add(images)
    permutation_pairs = list(itertools.product(itertools.permutations(range(2)), repeat=2))
    constructed = set()
    for row_permutations in permutation_pairs:
        for fibre_permutations in permutation_pairs:
            constructed.add(tuple((fibre_permutations[row_permutations[first][last]][first],
                                   row_permutations[first][last]) for first, last in indices))
    assert constructed == brute_force and len(brute_force) == math.factorial(2) ** 4 == 16
    return {'half_diagrams': 2, 'all_permutations_tested': 24,
            'complete_mappings': 16, 'parametrization_matches': True}


def verify_brandt_families():
    cases = []
    for rank in [2, 3]:
        permutations = list(itertools.permutations(range(rank)))
        for count in range(1, 5):
            triples = list(itertools.product(range(count), permutations, range(count)))
            negative_count = sum(sign(group) == -1 for first, group, last in triples)
            if count % 2:
                assert negative_count % 2 == 1
            else:
                multipliers, products = set(), set()
                for first, group, last in triples:
                    column_first, column_sign, column_last = even_map(first, sign(group), last, count)
                    assert column_first == last
                    column_group = ((0, 1) if column_sign == 1 else (1, 0)) if rank == 2 else lift_entry(tuple(range(rank)), group, column_sign)
                    multipliers.add((column_first, column_group, column_last))
                    products.add((first, compose(group, column_group), column_last))
                assert len(multipliers) == len(products) == len(triples)
            cases.append({'rank': rank, 'index_size': count, 'nonzero_elements': len(triples),
                          'negative_sign_elements': negative_count,
                          'complete_mapping_exists': count % 2 == 0})
    return cases


def main():
    subset_checks = []
    for rank, base in [(2, 6), (3, 7)]:
        for extension in range(4):
            degree = base + 4 * extension
            subsets = [frozenset(subset) for subset in itertools.combinations(range(degree), rank)]
            fixed = []
            for subset in subsets:
                partner = subset_partner(subset, degree, rank)
                assert len(partner) == rank
                assert subset_partner(partner, degree, rank) == subset
                if partner == subset:
                    fixed.append(subset)
                else:
                    assert len(subset & partner) == rank - 1
            expected = ({frozenset((0, 1)), frozenset((0, 2)), frozenset((1, 2))}
                        if rank == 2 else {frozenset((0, 1, 3)), frozenset((0, 2, 3)), frozenset((1, 2, 3))})
            assert set(fixed) == expected
            subset_checks.append({'degree': degree, 'rank': rank, 'subsets': len(subsets)})
    telephone = [1, 1]
    for size in range(2, 41):
        telephone.append(telephone[-1] + (size - 1) * telephone[-2])
        assert telephone[-1] % 2 == 0
    for degree in range(4, 41):
        if degree % 2 == 0:
            assert (math.comb(degree, 2) % 2 == 1) == (degree % 4 == 2)
        if degree % 2:
            assert (math.comb(degree, 3) % 2 == 1) == (degree % 4 == 3)
    lift_checks = 0
    for sandwich in itertools.permutations(range(3)):
        for input_sign in [1, -1]:
            fibre = [group for group in itertools.permutations(range(3)) if sign(group) == input_sign]
            for output_sign in [1, -1]:
                columns = [lift_entry(sandwich, group, output_sign) for group in fibre]
                products = [compose(compose(group, sandwich), column)
                            for group, column in zip(fibre, columns, strict=True)]
                assert len(set(columns)) == len(set(products)) == 3
                assert all(sign(column) == output_sign for column in columns)
                lift_checks += len(fibre)
    factors = [verify_factor(4, 2), verify_factor(5, 3),
               verify_factor(6, 2), verify_factor(7, 3),
               verify_factor(4, 2, True), verify_factor(4, 3, True),
               verify_factor(5, 2, True), verify_factor(5, 3, True)]
    counts = []
    for degree in range(1, 5):
        brauer = len(list(matchings(list(range(2 * degree)))))
        partial = len(list(matchings(list(range(2 * degree)), True)))
        assert partial == telephone[2 * degree]
        counts.append({'degree': degree, 'brauer_diagrams': brauer, 'partial_brauer_diagrams': partial})
    result = {'arithmetic': 'exact Python integers and permutations',
              'subset_pairing_checks': subset_checks,
              'telephone_count_parity': {'minimum': 2, 'maximum': 40},
              'binomial_parity_degrees': {'minimum': 4, 'maximum': 40},
              'symmetric_group_three_fibre_cases': lift_checks,
              'factor_bijections': factors, 'diagram_counts': counts,
              'small_degree_boundaries': verify_small_boundaries(),
              'rectangular_band_enumeration': verify_rectangular_enumeration(),
              'identity_sandwich_families': verify_brandt_families(),
              'scope': 'Finite instances of the constructions in the written proof.',
              'result': 'ALL_CHECKS_OK'}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
