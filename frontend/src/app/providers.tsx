'use client'

import { store } from '@/redux/store'
import { Provider } from 'react-redux'

export function Providers({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <Provider store={store}>
      {children}
    </Provider>
  )
}