#include <algorithm>
#include <compare>
#include <concepts>
#include <iostream>
#include <string>
#include <type_traits>

namespace std {

namespace details {

template <size_t offset, typename>
struct offset_index_sequence_impl {};

template <size_t offset, size_t... idxes>
struct offset_index_sequence_impl<offset, std::index_sequence<idxes...>> {
  using type = std::index_sequence<idxes + offset...>;
};

}  // namespace details

template <size_t offset, typename idxes>
using offset_index_sequence =
    typename details::offset_index_sequence_impl<offset, idxes>::type;

template <size_t offset, size_t N>
using make_offset_index_sequence =
    offset_index_sequence<offset, make_index_sequence<N>>;

}  // namespace std

namespace sequences {

template <size_t n>
struct string {
  static constexpr size_t size() noexcept { return n; }

  constexpr string(const char (&val)[n]) { std::copy_n(val, n, _value); }

  char _value[n];

  auto operator<=>(const string&) const = default;
};

namespace details {

//// Basic usual index variadic
namespace get {
template <size_t i, typename T0, typename... Ts>
struct f {
  using type = typename f<i - 1, Ts...>::type;
};

template <typename T0, typename... Ts>
struct f<0, T0, Ts...> {
  using type = T0;
};

template <size_t i, typename... Ts>
struct at {
  using type = typename f<i, Ts...>::type;
};

template <size_t i, size_t v0, size_t... vs>
struct f_v {
  static constexpr size_t value = f_v<i - 1, vs...>::value;
};

template <size_t v0, size_t... vs>
struct f_v<0, v0, vs...> {
  static constexpr size_t value = v0;
};

template <size_t i, size_t... vs>
static constexpr size_t at_v = f_v<i, vs...>::value;

}  // namespace get

template <size_t...>
struct strictly_ordered {
  static constexpr bool value = true;
};

template <size_t v0, size_t v1, size_t... rest>
struct strictly_ordered<v0, v1, rest...> {
  static constexpr bool value = v0 < v1 && strictly_ordered<v1, rest...>::value;
};

template <size_t... idxes>
static constexpr bool strictly_ordered_v = strictly_ordered<idxes...>::value;
}  // namespace details

// MARK: - `TypeSequence`

template <typename... Ts>
struct TypeSequence {};

template <>
struct TypeSequence<> {
  using This = TypeSequence<>;

  static constexpr size_t size() noexcept { return 0; }

  template <typename... Ts2>
  using append_t = TypeSequence<Ts2...>;

  template <typename... Ts2>
  using prepend_t = TypeSequence<Ts2...>;

  struct details {
    template <typename>
    struct concatenate {};

    template <typename... Ts2>
    struct concatenate<TypeSequence<Ts2...>> {
      using type = append_t<Ts2...>;
    };

    template <typename Seq, typename>
    struct select_impl {
      using type = Seq;
    };
  };

  template <typename T>
  using concatenate_t = typename details::template concatenate<T>::type;

  template <typename T>
  using select_t =
      typename details::template select_impl<TypeSequence<>, T>::type;
};

template <typename T0, typename... Ts>
struct TypeSequence<T0, Ts...> {
  using This = TypeSequence<T0, Ts...>;

  static constexpr size_t size() noexcept { return sizeof...(Ts) + 1; }

  template <typename... Ts2>
  using append_t = TypeSequence<T0, Ts..., Ts2...>;

  template <typename... Ts2>
  using prepend_t = TypeSequence<Ts2..., T0, Ts...>;

  struct details {
    template <size_t i>  // requires(i < size())  // fails in partial specialize
    struct get {
      using type = typename TypeSequence<Ts...>::template get_t<i - 1>;
    };

    template <>
    struct get<0> {
      using type = T0;
    };

    template <typename>
    struct concatenate {};

    template <typename... Ts2>
    struct concatenate<TypeSequence<Ts2...>> {
      using type = append_t<Ts2...>;
    };

    template <typename Seq, typename idxes>
    // requires(::sequences::details::strictly_ordered_v<idxes...>&&
    // ::sequences::
    //              details::get::at_v<sizeof...(idxes) - 1, idxes...> <
    //          size())
    struct select_impl {
      using type = Seq;
    };

    template <typename Seq, size_t i0, size_t... idxes>
    struct select_impl<Seq, std::index_sequence<i0, idxes...>> {
      using type = typename TypeSequence<Ts...>::details::template select_impl<
          Seq, std::index_sequence<i0 - 1, (idxes - 1)...>>::type;
    };

    template <typename Seq, size_t... idxes>
    struct select_impl<Seq, std::index_sequence<0, idxes...>> {
      using type = typename TypeSequence<Ts...>::details::template select_impl<
          typename Seq::template append_t<T0>,
          std::index_sequence<(idxes - 1)...>>::type;
    };

    template <size_t i, typename T>  // requires(i < size())  // fails partial
    struct set {
      using type = typename This::details::template select_impl<
          TypeSequence<>,
          std::make_index_sequence<i>>::type::template append_t<T>::
          template concatenate_t<typename This::details::template select_impl<
              TypeSequence<>,
              std::make_offset_index_sequence<i + 1, size() - i - 1>>::type>;
    };

    template <typename T>
    struct set<0, T> {
      using type = TypeSequence<T, Ts...>;
    };
  };

  template <size_t i>
  using get_t = typename details::template get<i>::type;

  template <typename T>
  using concatenate_t = typename details::template concatenate<T>::type;

  template <typename T>
  using select_t =
      typename details::template select_impl<TypeSequence<>, T>::type;

  template <size_t i, typename T>
  using set_t = typename details::template set<i, T>::type;

  using head_t = get_t<0>;
  using last_t = get_t<size() - 1>;
  using init_t = select_t<std::make_index_sequence<size() - 1>>;
  using tail_t = select_t<std::make_offset_index_sequence<1, size() - 1>>;
};

namespace tests {

// append
static_assert(std::same_as<typename TypeSequence<bool>::template append_t<int>,
                           TypeSequence<bool, int>>);
// prepend
static_assert(std::same_as<typename TypeSequence<int>::template prepend_t<bool>,
                           TypeSequence<bool, int>>);

// select
static_assert(std::same_as<typename TypeSequence<bool, char, int>::
                               template select_t<std::index_sequence<0, 2>>,
                           TypeSequence<bool, int>>);

// set at 0
static_assert(std::same_as<
              typename TypeSequence<bool, char, int>::template set_t<0, void>,
              TypeSequence<void, char, int>>);

// set at 1
static_assert(std::same_as<
              typename TypeSequence<bool, char, int>::template set_t<1, void>,
              TypeSequence<bool, void, int>>);

}  // namespace tests

// MARK: - Improved `index_sequence`

template <size_t... vals>
struct indices : std::index_sequence<vals...> {};

template <>
struct indices<> : std::index_sequence<> {
  using This = indices<>;

  static constexpr size_t size() noexcept { return 0; }

  /* static constexpr size_t string_size() noexcept { return 1; }

  static constexpr string<string_size()> to_string() noexcept {
    return string<1>("");
  }; */

  template <size_t... vals2>
  using append_t = indices<vals2...>;

  template <size_t... vals2>
  using prepend_t = indices<vals2...>;

  struct details {
    template <typename>
    struct concatenate {};

    template <size_t... vals2>
    struct concatenate<indices<vals2...>> {
      using type = append_t<vals2...>;
    };
    template <typename Seq, typename>
    struct select_impl {
      using type = Seq;
    };
  };

  template <typename T>
  using concatenate_t = typename details::template concatenate<T>::type;

  template <typename T>
  using select_t = typename details::template select_impl<indices<>, T>::type;
};

template <size_t v0, size_t... vals>
struct indices<v0, vals...> : std::index_sequence<vals...> {
  using This = indices<v0, vals...>;

  static constexpr size_t size() noexcept { return sizeof...(vals) + 1; }

  /* static constexpr size_t string_size() noexcept {
    static constexpr size_t new_string_size =
        std::string(std::to_string(v0) + (sizeof...(vals) == 0 ? "" : ", "))
            .size();
    return new_string_size + indices<vals...>::string_size();
  }

  static constexpr string<string_size()> to_string() noexcept { return 0; }; */

  template <size_t i>
  static constexpr size_t get() noexcept {
    return indices<vals...>::template get<i - 1>();
  }

  template <>
  static constexpr size_t get<0>() noexcept {
    return v0;
  }

  template <size_t... vals2>
  using append_t = indices<v0, vals..., vals2...>;

  template <size_t... vals2>
  using prepend_t = indices<vals2..., v0, vals...>;

  struct details {
    template <typename>
    struct concatenate {};

    template <size_t... vals2>
    struct concatenate<indices<vals2...>> {
      using type = append_t<vals2...>;
    };

    template <typename Seq, typename idxes>
    // requires(::sequences::details::strictly_ordered_v<idxes...>&&
    // ::sequences::
    //              details::get::at_v<sizeof...(idxes) - 1, idxes...> <
    //          size())
    struct select_impl {
      using type = Seq;
    };

    template <typename Seq, size_t i0, size_t... idxes>
    struct select_impl<Seq, std::index_sequence<i0, idxes...>> {
      using type = typename indices<vals...>::details::template select_impl<
          Seq, std::index_sequence<i0 - 1, (idxes - 1)...>>::type;
    };

    template <typename Seq, size_t... idxes>
    struct select_impl<Seq, std::index_sequence<0, idxes...>> {
      using type = typename indices<vals...>::details::template select_impl<
          typename Seq::template append_t<v0>,
          std::index_sequence<(idxes - 1)...>>::type;
    };

    template <size_t i, size_t new_v>  // requires(i < size())  // fails partial
    struct set {
      using type = typename This::details::template select_impl<
          indices<>,
          std::make_index_sequence<i>>::type::template append_t<new_v>::
          template concatenate_t<typename This::details::template select_impl<
              indices<>,
              std::make_offset_index_sequence<i + 1, size() - i - 1>>::type>;
    };

    template <size_t new_v>
    struct set<0, new_v> {
      using type = indices<new_v, vals...>;
    };
  };

  template <typename T>
  using select_t = typename details::template select_impl<indices<>, T>::type;

  template <typename T>
  using concatenate_t = typename details::template concatenate<T>::type;

  template <size_t i, size_t new_v>
  using set_t = typename details::template set<i, new_v>::type;

  static constexpr size_t head() noexcept { return get<0>(); }
  static constexpr size_t last() noexcept { return get<size() - 1>(); }
  using init_t = select_t<std::make_index_sequence<size() - 1>>;
  using tail_t = select_t<std::make_offset_index_sequence<1, size() - 1>>;
};

namespace details {

template <size_t N, size_t init>
struct init_indices_impl {
  using type = typename indices<init>::template concatenate_t<
      typename init_indices_impl<N - 1, init>::type>;
};

template <size_t init>
struct init_indices_impl<0, init> {
  using type = indices<>;
};

}  // namespace details

template <size_t N, size_t init>
using init_indices =
    typename details::template init_indices_impl<N, init>::type;

namespace tests {

// size
static_assert(indices<0>::size() == 1);
static_assert(indices<0, 1>::size() == 2);

// append
static_assert(
    std::same_as<typename indices<1>::template append_t<2>, indices<1, 2>>);
// prepend
static_assert(
    std::same_as<typename indices<2>::template prepend_t<1>, indices<1, 2>>);

// select
static_assert(
    std::same_as<
        typename indices<1, 2, 3>::template select_t<std::index_sequence<0, 2>>,
        indices<1, 3>>);

// set at 0
static_assert(std::same_as<typename indices<1, 2, 3>::template set_t<0, 0>,
                           indices<0, 2, 3>>);

// set at 1
static_assert(std::same_as<typename indices<1, 2, 3>::template set_t<1, 0>,
                           indices<1, 0, 3>>);

// init
static_assert(std::same_as<init_indices<1, 0>, indices<0>>);
static_assert(std::same_as<init_indices<2, 0>, indices<0, 0>>);

}  // namespace tests

namespace enumerate_simplexes_test {
// playing with constructions using this, the example being enumerating the
// (0 ... N); (0 ... N, 0 ... N - 1); ... (0 ... N 0 ... ... 0);

template <size_t N, typename Seq, bool dec_dim, bool terminate>
struct impl {};

// base case
template <size_t N>
struct impl<N, TypeSequence<>, true, false> {
  using type = typename impl<N, TypeSequence<indices<0>>, N == 1, N == 1>::type;
};

// increase dim case
template <size_t N, typename Seq>
struct impl<N, Seq, true, false> {
  static constexpr size_t m_dim() noexcept { return Seq::last_t::size(); }

  using type = typename impl<
      N, typename Seq::template append_t<init_indices<m_dim() + 1, 0>>, false,
      m_dim() == N>::type;
};

// general case
template <size_t N, typename Seq>
struct impl<N, Seq, false, false> {
  static constexpr size_t m_dim() noexcept { return Seq::last_t::size(); }

  template <size_t i>
  struct m_first_idx_non_max_impl {
    static constexpr size_t value = Seq::last_t::template get<i>() == N - i - 1
                                        ? m_first_idx_non_max_impl<i + 1>::value
                                        : i;
  };

  template <>
  struct m_first_idx_non_max_impl<m_dim()> {
    static constexpr size_t value = m_dim();
  };

  static constexpr size_t m_first_idx_non_max() noexcept {
    return m_first_idx_non_max_impl<0>::value;
  }

  template <size_t i>
  struct m_last_idx_non_max_impl {
    static constexpr size_t value = Seq::last_t::template get<i>() == N - i - 1
                                        ? m_last_idx_non_max_impl<i - 1>::value
                                        : i;
  };

  template <>
  struct m_last_idx_non_max_impl<0> {
    static constexpr size_t value = 0;
  };

  static constexpr size_t m_last_idx_non_max() noexcept {
    return m_last_idx_non_max_impl<m_dim() - 1>::value;
  }

  template <size_t idx0, size_t idx1, size_t dim, bool = idx0 == dim>
  struct match {};

  template <size_t idx0, size_t idx1, size_t dim>
  struct match<idx0, idx1, dim, false> {
    using type = typename impl<
        N,
        typename Seq::template append_t<
            typename Seq::last_t::template select_t<
                std::make_index_sequence<idx1>>::
                template append_t<Seq::last_t::template get<idx1>() + 1>::
                    template concatenate_t<init_indices<dim - idx1 - 1, 0>>>,
        false, false>::type;
  };

  template <size_t idx0, size_t idx1, size_t dim>
  struct match<idx0, idx1, dim, true> {
    using type = typename impl<N, Seq, true, dim == N>::type;
  };

  using type = typename match<m_first_idx_non_max(), m_last_idx_non_max(),
                              m_dim()>::type;
};

// terminal case
template <size_t N, typename Seq, bool dec_dim>
struct impl<N, Seq, dec_dim, true> {
  using type = Seq;
};

template <size_t N>
using enumerate_simplexes_t =
    typename impl<N, TypeSequence<>, true, N == 0>::type;

static_assert(std::same_as<enumerate_simplexes_t<0>, TypeSequence<>>);
static_assert(std::same_as<enumerate_simplexes_t<1>, TypeSequence<indices<0>>>);
static_assert(std::same_as<enumerate_simplexes_t<2>,
                           TypeSequence<indices<0>,
                                        indices<1>,
                                        indices<0, 0>,
                                        indices<1, 0>>>);
static_assert(std::same_as<enumerate_simplexes_t<3>,
                           TypeSequence<indices<0>,
                                        indices<1>,
                                        indices<2>,
                                        indices<0, 0>,
                                        indices<0, 1>,
                                        indices<1, 0>,
                                        indices<1, 1>,
                                        indices<2, 0>,
                                        indices<2, 1>,
                                        indices<0, 0, 0>,
                                        indices<0, 1, 0>,
                                        indices<1, 0, 0>,
                                        indices<1, 1, 0>,
                                        indices<2, 0, 0>,
                                        indices<2, 1, 0>>>);

}  // namespace enumerate_simplexes_test

}  // namespace sequences

int main(int argc, char* argv[]) {
  std::cout << "compiled!" << std::endl;
  return 0;
}
