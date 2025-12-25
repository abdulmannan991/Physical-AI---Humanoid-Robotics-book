/**
 * Custom Navbar Content
 *
 * Swizzled Docusaurus component to add authentication buttons.
 * This wraps the default navbar and adds our custom auth component.
 */

import React, { JSX } from 'react';
import Content from '@theme-original/Navbar/Content';
import { NavbarAuth } from '../../../components/Auth/NavbarAuth';
import type ContentType from '@theme/Navbar/Content';
import type {WrapperProps} from '@docusaurus/types';

type Props = WrapperProps<typeof ContentType>;

export default function ContentWrapper(props: Props): JSX.Element {
  return (
    <>
      <Content {...props} />
      <NavbarAuth />
    </>
  );
}
