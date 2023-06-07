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

template <typename... Ts>
struct TypeSequence {};

template <>
struct TypeSequence<> {
  using This = TypeSequence<>;

  static constexpr size_t length = 0;

  template <typename... Ts2>
  using append = TypeSequence<Ts2...>;

  template <typename... Ts2>
  using prepend = TypeSequence<Ts2...>;

  template <typename>
  struct concatenate {};

  template <typename... Ts2>
  struct concatenate<TypeSequence<Ts2...>> {
    using type = append<Ts2...>;
  };

  struct details {
    template <typename Seq, typename>
    struct select_impl {
      using type = Seq;
    };
  };
};

template <typename T0, typename... Ts>
struct TypeSequence<T0, Ts...> {
  using This = TypeSequence<T0, Ts...>;

  static constexpr size_t length = sizeof...(Ts) + 1;

  template <size_t i>  // requires(i < length)  // fails in partial specialize
  struct get {
    using type = typename TypeSequence<Ts...>::template get<i - 1>::type;
  };

  template <>
  struct get<0> {
    using type = T0;
  };

  template <typename... Ts2>
  using append = TypeSequence<T0, Ts..., Ts2...>;

  template <typename... Ts2>
  using prepend = TypeSequence<Ts2..., T0, Ts...>;

  template <typename>
  struct concatenate {};

  template <typename... Ts2>
  struct concatenate<TypeSequence<Ts2...>> {
    using type = append<Ts2...>;
  };

  struct details {
    template <typename Seq, typename idxes>
    // requires(::sequences::details::strictly_ordered_v<idxes...>&&
    // ::sequences::
    //              details::get::at_v<sizeof...(idxes) - 1, idxes...> <
    //          length)
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
          typename Seq::template append<T0>,
          std::index_sequence<(idxes - 1)...>>::type;
    };
  };

  template <size_t... idxes>
  using select = typename details::template select_impl<
      TypeSequence<>, std::index_sequence<idxes...>>::type;

  template <size_t i, typename T>  // requires(i < length)  // fails partial
  struct set {
    using type = typename This::details::template select_impl<
        TypeSequence<>,
        std::make_index_sequence<i>>::type::template append<T>::
        template concatenate<typename This::details::template select_impl<
            TypeSequence<>, std::make_offset_index_sequence<
                                i + 1, length - i - 1>>::type>::type;
  };

  template <typename T>
  struct set<0, T> {
    using type = TypeSequence<T, Ts...>;
  };
};

namespace tests {

// append
static_assert(std::same_as<typename TypeSequence<bool>::template append<int>,
                           TypeSequence<bool, int>>);
// prepend
static_assert(std::same_as<typename TypeSequence<int>::template prepend<bool>,
                           TypeSequence<bool, int>>);

// select
static_assert(
    std::same_as<typename TypeSequence<bool, char, int>::template select<0, 2>,
                 TypeSequence<bool, int>>);

// set at 0
static_assert(
    std::same_as<
        typename TypeSequence<bool, char, int>::template set<0, void>::type,
        TypeSequence<void, char, int>>);

// set at 1
static_assert(
    std::same_as<
        typename TypeSequence<bool, char, int>::template set<1, void>::type,
        TypeSequence<bool, void, int>>);

}  // namespace tests

}  // namespace sequences

int main(int argc, char* argv[]) {
  std::cout << "hello, world!" << std::endl;
  return 0;
}
